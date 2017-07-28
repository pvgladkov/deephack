import numpy as np
import pandas as pd
from turing.features.common import desctiptive_stats, basestat_series
from collections import Counter
import json

# DEPS_OPTIONS = json.load(open("data/deps_list.json", "r"))

def _find_root(sentence):
    for token in sentence:
        if token.dep_ == "ROOT":
            return token

    raise ValueError()


def _depth(node):
    return 1 + np.max([_depth(child) for child in node.children])


def _depth_up(node):
    if node.dep_ == "ROOT":
        return 0

    return 1 + _depth_up(node.head)


def syntax_stats(nlp_context, nlp_response):
    def depth_stats(nlp_sentence):
        stats = desctiptive_stats([_depth_up(x) for x in nlp_sentence])
        stats.index = map(lambda x: "syntax_depth_{}".format(x), stats.index)
        return stats

    def child_stats(nlp_sentence):
        stats = desctiptive_stats([len(list(x.children)) for x in nlp_sentence])
        stats.index = map(lambda x: "syntax_children_{}".format(x), stats.index)
        return stats

    def dependency_stats(nlp_sentence):
        counter = Counter()
        for token in nlp_sentence:
            for dep in token.dep_.split("||"):
                counter[dep] += 1

        abs_counts = pd.Series(data=[counter[pos] for pos in DEPS_OPTIONS],
                               index=["syntax_{}_abs".format(pos) for pos in DEPS_OPTIONS])

        relative_counts = pd.Series(data=[float(counter[pos]) / len(nlp_sentence) for pos in DEPS_OPTIONS],
                                    index=["syntax_{}_rel".format(pos) for pos in DEPS_OPTIONS])

        return abs_counts.append(relative_counts)

    res = pd.Series()
    res = res.append(basestat_series(depth_stats)(nlp_context, nlp_response))
    res = res.append(basestat_series(child_stats)(nlp_context, nlp_response))
    res = res.append(basestat_series(dependency_stats)(nlp_context, nlp_response))

    return res