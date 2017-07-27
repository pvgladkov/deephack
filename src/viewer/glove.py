#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
import os
import os.path
import subprocess
import sys
from tempfile import NamedTemporaryFile

assert sys.version_info >= (3, 6), 'Python 3.6 or higher required'


def get_temp_fname():
    """
    Get a name of a temporary file.
    """
    tfile = NamedTemporaryFile(delete=False)
    tfile.close()
    return tfile.name


class Glove(object):
    """
    Wrapper for GloVe binaries.
    """

    def __init__(self, bin_dir=None):
        self.binaries = {}
        for i in ('vocab_count', 'cooccur', 'shuffle', 'glove'):
            if bin_dir is not None:
                self.binaries[i] = os.path.join(bin_dir, i)
            else:
                self.binaries[i] = i

    def vocab_count(self, corpus_fname, vocab_fname, min_count, max_vocab):
        """
        Given a name of a corpus file, launch vocab_count and write its result
        to the specified output vocabular file.

        `min_count` specifies the lower threshold for word occurrences
        `max_vocab` specifies the upper bound on vocabulary size
        """
        with open(corpus_fname) as corpus_file, \
                open(vocab_fname, 'w') as vocab_file, \
                open(os.devnull, 'w') as devnull:
            args = [self.binaries['vocab_count'], '-min-count', str(min_count),
                    '-max-vocab', str(max_vocab)]
            subprocess.run(args, stdin=corpus_file, stdout=vocab_file,
                           stderr=devnull, check=True)

    def cooccur(self, corpus_fname, vocab_fname, cooccur_fname, symmetric,
                window_size):
        """
        Given names of a corpus file and a vocabulary counts file, calculate
        word-word cooccurrence statistics and write them to the specified file.

        `symmetric` specifies whether to use only left or left and right
        contexts
        `window_size` specifies the number of context words
        """
        with open(corpus_fname) as corpus_file, \
                open(cooccur_fname, 'w') as cooccur_file, \
                open(os.devnull, 'w') as devnull:
            args = [self.binaries['cooccur'], '-symmetric', str(symmetric),
                    '-window-size', str(window_size), '-vocab-file',
                    vocab_fname]
            subprocess.run(args, stdin=corpus_file, stdout=cooccur_file,
                           stderr=devnull, check=True)

    def shuffle(self, cooccur_fname, output_fname):
        """
        Given a name of the word-word cooccurence statistics file, shuffle it
        and write the result to the speficied output file.
        """
        with open(cooccur_fname) as cooccur_file, \
                open(output_fname, 'w') as output_file, \
                open(os.devnull, 'w') as devnull:
            args = [self.binaries['shuffle']]
            subprocess.run(args, stdin=cooccur_file, stdout=output_file,
                           stderr=devnull, check=True)

    def glove(self, cooccur_fname, vocab_fname, vector_fname, grad_fname,
              vector_size, alpha=0.75, xmax=100.0, eta=0.05, iter_num=100,
              model=2, num_threads=1):
        """
        Launch glove with the specified names of the word-word cooccurence
        file, the vocabulary count file, the output vector file, the output
        gradient file, the specified vector size, alpha, xmax, iter and eta
        parameters and the model type.
        """
        args = [self.binaries['glove'], '-input-file', cooccur_fname,
                '-vocab-file', vocab_fname, '-save-file', vector_fname,
                '-gradsq-file', grad_fname, '-vector-size', str(vector_size),
                '-alpha', str(alpha), '-xmax', str(xmax), '-eta', str(eta),
                '-model', str(model), '-iter', str(iter_num), '-binary', '0',
                '-threads', str(num_threads)]
        with open(os.devnull, 'w') as devnull:
            subprocess.run(args, stderr=devnull, check=True)

    def auto_glove(self, corpus_fname, output_fname, glove_options={}):
        """
        Launch consecutive GloVe stages using temporary files for keeping
        intermediate data.

        Options are passed via dictionary `glove_options` with the following
        keys: `min_occur` (default: 1), 'vec_size` (default: 50), `symmetric`
        (default: 0), `window_size` (default: 5), `num_iter` (default: 1000),
        `xmax` (default: 100), `eta` (default: 0.05)
        """
        # specify default values for missing options
        default_values = {'min_occur': 1,
                          'vec_size': 50,
                          'symmetric': 0,
                          'window_size': 5,
                          'num_iter': 1000,
                          'xmax': 100,
                          'eta': 0.05}
        for k, v in default_values.items():
            if k not in glove_options:
                glove_options[k] = v

        temp_vocab = get_temp_fname()
        temp_occur = get_temp_fname()
        temp_shuffled = get_temp_fname()

        try:
            # step 1: create the vocabulary counts file
            self.vocab_count(corpus_fname, temp_vocab,
                             glove_options['min_occur'],
                             10000)

            # step 2: create the word-word occurrence file
            self.cooccur(corpus_fname, temp_vocab, temp_occur,
                         glove_options['symmetric'],
                         glove_options['window_size'])

            # step 3: shuffle the occurrences
            self.shuffle(temp_occur, temp_shuffled)

            # step 4: produce GloVe vectors
            output_prefix = os.path.splitext(output_fname)[0]
            self.glove(temp_occur, temp_vocab, output_prefix + '_vec',
                       output_prefix + '_grad', glove_options['vec_size'],
                       0.75, glove_options['xmax'], glove_options['eta'],
                       glove_options['num_iter'])
        finally:
            for fname in (temp_vocab, temp_occur, temp_shuffled):
                if os.path.isfile(fname):
                    os.unlink(fname)


def load_vectors(filename):
    """
    Load word vectors by GloVe from the specified file.
    """
    word_vec = {}
    with open(filename) as vec_file:
        for line in vec_file:
            word, vec = line.split(None, maxsplit=1)
            vec = np.array(list(map(float, vec.split())))
            word_vec[word] = vec

    return word_vec
