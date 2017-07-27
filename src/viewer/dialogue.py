#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import sys
from collections import namedtuple
from cucco import Cucco

assert sys.version_info >= (3, 6), 'Python 3.6 or higher required'


Dialogue = namedtuple('Dialogue', ['context', 'id', 'evaluation', 'thread',
                                   'users'])
Evaluation = namedtuple('Evaluation', ['Alice', 'Bob'])
Thread = namedtuple('Thread', ['text', 'userId', 'time'])
User = namedtuple('User', ['Alice', 'Bob'])


def dialogue_iterator(filename, test=False, raw=False):
    """
    Iterate dialogues in the specified file.

    One may specify whether to read a test dataset (without evaluation scores
    and user types) and to return raw dialogue phrases (without
    postprocessing).
    """

    cu = Cucco()
    normalizations = [
        'remove_accent_marks',
        ('replace_emojis', {'replacement': ' '}),
        ('replace_hyphens', {'replacement': ''}),
        ('replace_punctuation', {'replacement': ''}),
        ('replace_urls', {'replacement': ' '}),
        'remove_extra_whitespaces'
    ]

    with open(filename) as input_file:
        for r in json.load(input_file):
            if not raw:
                r['context'] = cu.normalize(r['context'])
            # form the thread list
            th_list = []
            for i in r['thread']:
                if not raw:
                    i['text'] = i['text'].rstrip()
                    if not i['text']:
                        continue
                    i['text'] = cu.normalize(i['text'], normalizations)
                    i['text'] = i['text'].lower()
                th_list.append(Thread(i['text'], i['userId'], i.get('time')))

            # if we're dealing with the test dataset, do not return user types
            # and evaluation scores
            if test:
                d = Dialogue(r['context'], r['dialogId'], None, th_list, None)
            else:
                # form the evaluation dictionary
                ev_dict = {}
                for i in r['evaluation']:
                    if i['userId'] == 'Alice':
                        ev_dict['Alice'] = i['quality']
                    elif i['userId'] == 'Bob':
                        ev_dict['Bob'] = i['quality']
                    else:
                        raise ValueError('incorrect user ID')
                # form the user list
                us_dict = {}
                for i in r['users']:
                    if i['id'] == 'Alice':
                        us_dict['Alice'] = i['userType']
                    elif i['id'] == 'Bob':
                        us_dict['Bob'] = i['userType']
                    else:
                        raise ValueError('incorrect user ID')
                d = Dialogue(r['context'], r['dialogId'],
                             Evaluation(ev_dict['Alice'], ev_dict['Bob']),
                             th_list,
                             User(us_dict['Alice'], us_dict['Bob']))
            yield concat_phrases(d)


def is_bot_dialogue(d):
    """
    Detect whether there is a bot among speakers
    """
    return d.users.Alice == 'Bot' or d.users.Bob == 'Bot'


def get_bot_id(d):
    """
    Get bot's ID

    Returns None if there are no bots in the dialogue.
    """
    if d.users.Alice == 'Bot':
        return 'Alice'
    elif d.users.Bob == 'Bot':
        return 'Bob'
    else:
        return None


def get_speaker_seq(d, bot_based=False):
    """
    Return sequence of speaker IDs

    Set bot_based to get the sequence of human-bot labels.
    """
    if bot_based:
        letters = {'Alice': 'H', 'Bob': 'H'}
        bot_id = get_bot_id(d)
        if bot_id is not None:
            letters[get_bot_id(d)] = 'B'
    else:
        letters = {'Alice': 'A', 'Bob': 'B'}

    seq = [letters[th.userId] for th in d.thread]
    return ''.join(seq)


def concat_phrases(d):
    """
    Concatenate consecutive phrases from the same speaker.abs
    """
    if len(d.thread) < 2:
        return d

    result = []
    cur_phrase = d.thread[0].text
    cur_user = d.thread[0].userId
    cur_time = d.thread[0].time

    for p in d.thread[1:]:
        if p.userId == cur_user:
            cur_phrase = cur_phrase + ' ' + p.text
        else:
            result.append(Thread(cur_phrase, cur_user, cur_time))
            cur_phrase = p.text
            cur_user = p.userId
        cur_time = p.time

    # process the last phrase
    result.append(Thread(cur_phrase, cur_user, cur_time))

    return Dialogue(d.context, d.id, d.evaluation, result, d.users)
