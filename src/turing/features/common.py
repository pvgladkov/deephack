from turing.features import nlp
import pandas as pd
import scipy
import numpy as np


def human_readable(text):
    return text.replace("@@ ", "")


def tokenize(text):
    return text.split(' ')


def split_by_phrases(tokens):
    res = []
    curr_phrase = []
    for token in tokens:
        if token.endswith("speaker>"):
            if curr_phrase:
                res.append(curr_phrase)
                curr_phrase = []
        else:
            curr_phrase.append(token)

    if curr_phrase:
        res.append(curr_phrase)

    return res


def parse_and_flatten(tokens):
    cleaned = [token for phrase in split_by_phrases(tokens) for token in phrase if not token.startswith("<")]
    parsed = [nlp(unicode(x)) for x in cleaned]
    return [x for doc in parsed for x in doc]


def join_sentence(tokens):
    phrases = split_by_phrases(tokens)
    filtered = map(lambda x: [y for y in x if not y.startswith("<")], phrases)
    glued = map(lambda x: " ".join(x), filtered)

    return unicode(".".join(glued))


def basestat(f, label):
    def target(context, response):
        response_value = f(response)
        context_value = f(context)
        if context_value and response_value:
            ratio = float(response_value) / context_value
        else:
            ratio = 0
            
        return pd.Series([context_value, response_value, ratio],
                         index=["context_{}".format(label), "response_{}".format(label), "ratio_{}".format(label)])

    return target


def basestat_series(f):
    def target(context, response):
        if context and response:
            response_ser = f(response)
            context_ser = f(context)

            response_ser.index = map(lambda x: "response_{}".format(x), response_ser.index)
            context_ser.index = map(lambda x: "context_{}".format(x), context_ser.index)

            return response_ser.append(context_ser)
        else:
            return pd.Series()

    return target


def desctiptive_stats(arr):
    stats = scipy.stats.describe(arr).__dict__
    min_val, max_val = stats["minmax"]
    stats["min"] = min_val
    stats["max"] = max_val
    stats["median"] = np.median(arr)
    del stats["minmax"]

    ser = pd.Series.from_array(stats)
    return ser