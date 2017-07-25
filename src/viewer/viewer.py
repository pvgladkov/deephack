#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import curses
import json
import logging
import os.path
import random
import sys
from collections import namedtuple

assert sys.version_info >= (3, 6), 'Python 3.6 or higher required'

logging.basicConfig()
logger = logging.getLogger(__name__)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Interactive dialogue viewer')
    parser.add_argument('input_file', help='dialogue input file in the JSON '
                        'format')

    p_args = parser.parse_args()
    if not os.path.isfile(p_args.input_file):
        logger.error('incorrect file name %s', p_args.input_file)
        sys.exit(1)

    return p_args


def dialogue_iterator(filename):
    """
    Given a name of a JSON file with dialogues, iterate through its records.
    """
    Dialogue = namedtuple('Dialogue', ['context', 'id', 'thread', 'is_bot'])

    with open(filename) as input_file:
        for record in json.load(input_file):
            d = Dialogue(record['context'],
                         record['dialogId'],
                         record['thread'],
                         set(u['id'] for u in record['users']
                             if u['userType'] == 'Bot'))
            yield d


def dialogue_list(filename):
    """
    Given a name of a JSON file with dialogues, return the list of its records.
    """
    Dialogue = namedtuple('Dialogue', ['context', 'id', 'thread', 'is_bot'])

    results = []
    with open(filename) as input_file:
        for record in json.load(input_file):
            d = Dialogue(record['context'],
                         record['dialogId'],
                         record['thread'],
                         set(u['id'] for u in record['users']
                             if u['userType'] == 'Bot'))
            results.append(d)

    return results


def viewer(screen, args):
    """
    The main function of the program.
    """
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)

    d_list = dialogue_list(args.input_file)
    random.shuffle(d_list)
    for d in d_list:
        screen.addstr('# {} \n\n'.format(d.id), curses.A_BLINK)
        screen.addstr(d.context + '\n\n', curses.A_BOLD)

        for p in d.thread:
            if d.is_bot:
                screen.addstr(p['text'].strip() + ' - ', curses.color_pair(1)
                              if p['userId'] in d.is_bot else
                              curses.color_pair(0))
            else:
                screen.addstr(p['text'].strip() + ' - ', curses.color_pair(2)
                              if p['userId'] == 'Bob' else
                              curses.color_pair(0))

        if len(d.thread) > 2 and len(set(p['userId'] for p in d.thread)) > 1:
            screen.getch()
        screen.clear()


if __name__ == '__main__':
    args = parse_args()
    try:
        curses.wrapper(viewer, args)
    except KeyboardInterrupt:
        pass
