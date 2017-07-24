import numpy as np
import pandas as pd
from turing.features.common import desctiptive_stats, basestat_series


def word2vec_stats(nlp_context, nlp_response):
    def avg_vector(nlp_sentence):
        arr = np.array([x.vector for x in nlp_sentence])

        if arr.size > 0:
            w2v = np.mean(arr, axis=0)
            return pd.Series(data=w2v,
                             index=["w2v_{}".format(i) for i in range(0, w2v.shape[0])])
        else:
            return pd.Series()

    def corr_stats(nlp_sentence):
        corrs = []
        for i in range(0, len(nlp_sentence) - 1):
            for j in range(i + 1, len(nlp_sentence)):
                corrs.append(nlp_sentence[i].similarity(nlp_sentence[j]))

        if corrs:
            stats = desctiptive_stats(corrs)
            stats.index = map(lambda x: "w2v_correlations_{}".format(x), stats.index)
            return stats
        else:
            return pd.Series()

    res = pd.Series()
    res = res.append(basestat_series(avg_vector)(nlp_context, nlp_response))
    #     res = res.append(basestat_series(corr_stats)(nlp_context, nlp_response))

    return res

