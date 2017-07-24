from turing.features.common import basestat
from spacy import en
import pandas as pd
import numpy as np
import math
import nltk
from turing.features import nlp
from collections import Counter


def lenstat(context, response):
    return basestat(len, "length")(context, response)


def stopwords_stat(context, response):
    def stopword_count(text):
        return len(filter(lambda x: x.lower() in en.STOP_WORDS, text))

    return basestat(stopword_count, "stopwords")(context, response)


def _read_vocab():
    tokens = nltk.corpus.brown.words()
    parsed = [nlp(unicode(y)) for y in tokens]
    chained = [x for doc in parsed for x in doc]

    lemmas = [x.lemma_ for x in [y for y in chained] if x.is_alpha]
    words = [x.orth_.lower() for x in [y for y in chained] if x.is_alpha]

    lemma_counts = Counter(lemmas)
    word_counts = Counter(words)

    return word_counts, lemma_counts

word_counts, lemma_counts = _read_vocab()
# word_counts, lemma_counts = Counter(), Counter()
top_words = dict(word_counts.most_common(5000))
top_lemmas = dict(lemma_counts.most_common(5000))

freq_idx_lemmas = {lemma: idx for idx, (lemma, cnt) in enumerate(lemma_counts.iteritems())}


def freq_stat(parsed_context, parsed_response):

    def topN_count(parsed_text):
        return len(filter(lambda x: x.orth_.lower() in top_words, parsed_text))

    def topN_count_lemma(parsed_text):
        return len(filter(lambda x: x.lemma_ in top_lemmas, parsed_text))

    def no_vocab_tokens(parsed_text):
        return len(filter(lambda x: x.lemma_ not in lemma_counts, parsed_text))

    def avg_index_lemma(parsed_text):
        freqs = [freq_idx_lemmas.get(token.lemma_, None) for token in parsed_text]
        logs = [math.log(x) for x in filter(lambda x: x, freqs)]
        if logs:
            return np.mean(logs)
        else:
            return None

    res = pd.Series()

    if parsed_context and parsed_response:
        res = res.append(basestat(topN_count, "topN_tokens_count")(parsed_context, parsed_response))
        res = res.append(basestat(lambda x: float(topN_count(x)) / len(x), "topN_tokens_count_relative")(parsed_context,
                                                                                                         parsed_response))
        res = res.append(basestat(topN_count_lemma, "topN_count_lemma")(parsed_context, parsed_response))
        res = res.append(
            basestat(lambda x: float(topN_count_lemma(x)) / len(x), "topN_count_lemma_relative")(parsed_context,
                                                                                                 parsed_response))
        res = res.append(basestat(no_vocab_tokens, "no_vocab_tokens")(parsed_context, parsed_response))
        res = res.append(
            basestat(lambda x: float(no_vocab_tokens(x)) / len(x), "no_vocab_tokens_relative")(parsed_context,
                                                                                               parsed_response))
        res = res.append(basestat(avg_index_lemma, "avg_index_lemma")(parsed_context, parsed_response))

    return res


def special_terms_stat(context, response):
    def spec_count(term, text):
        return len([x for x in text if x == "<{}>".format(term)])

    res = pd.Series()
    res = res.append(basestat(lambda x: spec_count("at", x), "mentions")(context, response))
    res = res.append(basestat(lambda x: spec_count("number", x), "numbers")(context, response))
    res = res.append(basestat(lambda x: spec_count("url", x), "links")(context, response))
    return res