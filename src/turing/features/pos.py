from collections import Counter
import pandas as pd
from turing.features.common import basestat_series

POS_OPTIONS = ["ADJ","ADP","ADV","AUX","CCONJ","DET","INTJ","NOUN","NUM","PART","PRON","PROPN","PUNCT","SCONJ",
               "SYM","VERB","X"]


def pos_stats(parsed_context, parsed_response):
    def tag(parsed):

        if parsed:
            counter = Counter()
            for token in parsed:
                counter[token.pos_] += 1

            abs_counts = pd.Series(data=[counter[pos] for pos in POS_OPTIONS],
                                   index=["pos_{}_abs".format(pos) for pos in POS_OPTIONS])

            relative_counts = pd.Series(data=[float(counter[pos]) / len(parsed) for pos in POS_OPTIONS],
                                        index=["pos_{}_rel".format(pos) for pos in POS_OPTIONS])

            return abs_counts.append(relative_counts)
        else:
            return pd.Series()

    return basestat_series(tag)(parsed_context, parsed_response)