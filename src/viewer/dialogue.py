#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import sys
from collections import namedtuple

assert sys.version_info >= (3, 6), 'Python 3.6 or higher required'


def dialogue_iterator(filename, test=False):
    """
    Iterate dialogues in the specified file.
    """
    Dialogue = namedtuple('Dialogue', ['context', 'id', 'evaluation', 'thread',
                                       'users'])
    Evaluation = namedtuple('Evaluation', ['Alice', 'Bob'])
    Thread = namedtuple('Thread', ['text', 'userId'])
    User = namedtuple('User', ['Alice', 'Bob'])

    with open(filename) as input_file:
        for r in json.load(input_file):
            # form the thread list
            th_list = []
            for i in r['thread']:
                th_list.append(Thread(i['text'], i['userId']))

            # if we're dealing with the test dataset, do not return user types
            # and evaluation scores
            if test:
                yield Dialogue(r['context'], r['dialogId'], None, th_list,
                               None)
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
                yield d


def is_bot_dialogue(d):
    return d.users.Alice == 'Bot' or d.users.Bob == 'Bot'
