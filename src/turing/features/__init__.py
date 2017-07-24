import json
import spacy

nlp = spacy.load('en')

from freq import special_terms_stat, stopwords_stat, freq_stat, lenstat
from pos import pos_stats
from syntax import syntax_stats
from w2v import word2vec_stats