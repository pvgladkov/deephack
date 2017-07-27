#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import curses
import dialogue as dl
import logging
import os.path
import random
import sys

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


def viewer(screen, args):
    """
    The main function of the program.
    """
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)

    d_list = list(dl.dialogue_iterator(args.input_file, raw=True))
    random.shuffle(d_list)
    for d in d_list:
        screen.addstr('# {} \n\n'.format(d.id), curses.A_BLINK)
        screen.addstr(d.context + '\n\n', curses.A_BOLD)

        if dl.is_bot_dialogue(d):
            bot_id = dl.get_bot_id(d)
            for p in d.thread:
                screen.addstr(p.text.strip() + ' - ', curses.color_pair(1)
                              if p.userId == bot_id else curses.color_pair(0))
        else:
            for p in d.thread:
                screen.addstr(p.text.strip() + ' - ', curses.color_pair(2)
                              if p.userId == 'Bob' else curses.color_pair(0))

        if len(d.thread) > 2 and len(set(p.userId for p in d.thread)) > 1:
            screen.getch()
        screen.clear()


if __name__ == '__main__':
    args = parse_args()
    try:
        curses.wrapper(viewer, args)
    except KeyboardInterrupt:
        pass
