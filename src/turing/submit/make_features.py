import os
import json
import pandas as pd
import numpy as np
from turing.features import nlp
from turing.features.freq import top_words, top_lemmas, lemma_counts, freq_idx_lemmas

from sklearn.metrics.pairwise import cosine_similarity
import math
from turing.submit.utils import get_score
import argparse

def ngram_ppl(diag, user, ppl_df):
    res = pd.Series()

    res["self_ngram_logprob2"] = np.mean(
        ppl_df[ppl_df.dialogId == diag["dialogId"]][ppl_df.userId == user]["logprob"])
    res["self_ngram_ppl"] = np.mean(
        ppl_df[ppl_df.dialogId == diag["dialogId"]][ppl_df.userId == user]["ppl"])
    res["other_ngram_logprob"] = np.mean(
        ppl_df[ppl_df.dialogId == diag["dialogId"]][ppl_df.userId != user]["logprob"])
    res["other_ngram_ppl"] = np.mean(
        ppl_df[ppl_df.dialogId == diag["dialogId"]][ppl_df.userId != user]["ppl"])

    return res


def lengths(diag, user):
    res = pd.Series()
    self_thread = filter(lambda x: x["userId"] == user, diag["thread"])
    other_thread = filter(lambda x: x["userId"] != user, diag["thread"])
    res["self_phrases_cnt"] = len(self_thread)
    res["other_phrases_cnt"] = len(other_thread)

    res["self_words_cnt"] = len([w for s in self_thread for w in s])
    res["other_words_cnt"] = len([w for s in other_thread for w in s])

    res["self_avg_words"] = 0 if res["self_phrases_cnt"] == 0 else float(res["self_words_cnt"]) / res[
        "self_phrases_cnt"]
    res["other_avg_words"] = 0 if res["other_phrases_cnt"] == 0 else float(res["other_words_cnt"]) / res[
        "other_phrases_cnt"]

    return res


def context_similarity(diag, user):
    context_vector = np.mean([
        word.vector for word in nlp(diag["context"])
    ], axis=0).reshape((1, -1))

    self_thread = filter(lambda x: x["userId"] == user, diag["thread"])
    other_thread = filter(lambda x: x["userId"] != user, diag["thread"])

    try:
        self_vector = np.mean([
            word.vector for word in nlp(unicode(self_thread[0]["text"]))
        ], axis=0).reshape((1, -1))

        other_vector = np.mean([
            word.vector for word in nlp(unicode(other_thread[0]["text"]))
        ], axis=0).reshape((1, -1))

        res = pd.Series()

        res["self_context_cosine"] = 0 if not self_thread else cosine_similarity(self_vector, context_vector).flatten()[
            0]
        res["other_context_cosine"] = 0 if not other_thread else \
        cosine_similarity(other_vector, context_vector).flatten()[0]
        return res
    except:
        return pd.Series()


def w2v(diag, user):
    self_thread = filter(lambda x: x["userId"] == user, diag["thread"])
    other_thread = filter(lambda x: x["userId"] != user, diag["thread"])

    try:
        self_vector = np.mean([
            word.vector for word in nlp(unicode(" ".join([x["text"] for x in self_thread])))
        ], axis=0)

        other_vector = np.mean([
            word.vector for word in nlp(unicode(" ".join([x["text"] for x in other_thread])))
        ], axis=0)

        self_ser = pd.Series(data=self_vector, index=["self_w2v_{}".format(i) for i in range(0, self_vector.shape[0])])
        other_ser = pd.Series(data=other_vector,
                              index=["other_w2v_{}".format(i) for i in range(0, other_vector.shape[0])])
        return self_ser.append(other_ser)
    except:
        return pd.Series()


def freq_stat(diag, user):
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
    self_thread = [nlp(unicode(x)) for x in filter(lambda x: x["userId"] == user, diag["thread"])]
    other_thread = [nlp(unicode(x)) for x in filter(lambda x: x["userId"] != user, diag["thread"])]

    res["self_topN_count"] = np.mean([
        topN_count(x) for x in self_thread
    ])
    res["other_topN_count"] = np.mean([
        topN_count(x) for x in other_thread
    ])

    res["self_no_vocab_tokens"] = np.mean([
        no_vocab_tokens(x) for x in self_thread
    ])
    res["other_no_vocab_tokens"] = np.mean([
        no_vocab_tokens(x) for x in other_thread
    ])

    avg_idx_self = filter(lambda x: x, [avg_index_lemma(x) for x in self_thread])
    avg_idx_other = filter(lambda x: x, [avg_index_lemma(x) for x in other_thread])

    if avg_idx_self:
        res["self_avg_index_lemma"] = np.mean(avg_idx_self)

    if avg_idx_other:
        res["other_avg_index_lemma"] = np.mean(avg_idx_other)

    return res


def make_features(diags, ppl_df, labeled=False):
    observations = []
    for d in diags:
        for name in ("Bob", "Alice"):
            obs = freq_stat(d, name) \
                .append(lengths(d, name)) \
                .append(context_similarity(d, name)) \
                .append(w2v(d, name)) \
                .append(ngram_ppl(d, name, ppl_df))

            obs["user"] = name
            obs["dialogId"] = d["dialogId"]

            if labeled:
                obs["label"] = get_score(d, name)

            observations.append(obs)

    return pd.DataFrame(observations)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-p', '--ppl', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    args = parser.parse_args()

    diags = json.load(open(args.input))
    ppl_df = pd.DataFrame.from_csv(args.ppl).reset_index()

    all_features = make_features(diags, ppl_df)
    all_features.to_csv(args.output)