#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import logging
import os.path
import re
import sys
from viewer import dialogue_iterator

assert sys.version_info >= (3, 6), 'Python 3.6 or higher required'

logging.basicConfig()
logger = logging.getLogger(__name__)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Convert dialogues to the '
                                     'plain-text format')
    parser.add_argument('input_file', help='JSON dialogue file')
    parser.add_argument('-c', '--context', action='store_true',
                        help='include context in output')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep non-alphabetic characters')

    p_args = parser.parse_args(args)
    if not os.path.isfile(p_args.input_file):
        logger.error('incorrect input file specified')
        sys.exit(1)

    return p_args


def dialogue2txt(input_fname, print_context=False, keep_nonalpha=False):
    """
    Given a JSON dialogue file name, print its contents in the plain-text
    format.
    """
    if keep_nonalpha:
        def preprocess(s):
            return str.lower(s)
    else:
        def preprocess(s):
            regex = re.compile('[^a-zA-Z ]')
            return str.lower(regex.sub('', s))

    for d in dialogue_iterator(input_fname):
        if print_context:
            print(preprocess(d.context))
        for p in d.thread:
            print(preprocess(p['text']))


if __name__ == '__main__':
    args = parse_args()
    dialogue2txt(args.input_file, args.context)
