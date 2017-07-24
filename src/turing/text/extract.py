from turing.features import *
import pandas as pd
from turing.features.common import human_readable, tokenize, join_sentence
import argparse
import logging
import os

logger = logging.getLogger(__name__)

plain_funcs = [lenstat, stopwords_stat, special_terms_stat]
nlp_funcs = [freq_stat, pos_stats, syntax_stats, word2vec_stats]


def one_line(ser, funcs, nlp_funcs):
    res = pd.Series()
    for f in funcs:
        res = res.append(f(ser["context"], ser["response"]))

    for f in nlp_funcs:
        res = res.append(f(ser["nlp_context"], ser["nlp_response"]))
    return res


def run(inpath, outpath, lower_bound=None, upper_bound=None):
    logger.info("Loading csv")
    train = pd.DataFrame.from_csv(inpath, sep='\t', header=-1)[lower_bound:upper_bound]
    train.columns = ["context","response",	"human-generated"]
    train["context"] = train["context"].map(human_readable).map(tokenize)
    train["response"] = train["response"].map(human_readable).map(tokenize)

    logger.info("Parsing nlp")

    train["nlp_context"] = train["context"].map(lambda x: nlp(join_sentence(x)))
    train["nlp_response"] = train["response"].map(lambda x: nlp(join_sentence(x)))

    logger.info("applying features")

    features = train.apply(lambda x: one_line(x, plain_funcs, nlp_funcs), axis=1)
    features.to_csv(outpath)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-l', '--lower', type=int, default=None)
    parser.add_argument('-u', '--upper', type=int, default=None)

    args = parser.parse_args()
    print args.lower, args.upper

    for file in os.listdir(args.input_dir):
        run(os.path.join(args.input_dir,file), "{}_{}".format(args.output,file))


