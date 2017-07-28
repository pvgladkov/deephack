import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, LeavePOut
from scipy.stats import spearmanr
from collections import Counter
from sklearn.model_selection import train_test_split
import argparse
import xgboost as xgb
from turing.submit.utils import df_to_submit

def reg_to_binary(df):
    dfa = df.copy()
    dfa["merge"] = 1
    large_df = pd.merge(dfa, dfa, on="merge")

    return large_df


def to_order(df, bst):
    features = df.drop([ "dialogId_x", "dialogId_y", "user_x", "user_y"], axis=1)
    dtest = xgb.DMatrix(features.values, feature_names=features.columns)
    df["prediction"] = bst.predict(dtest)

    counter = Counter()

    for gr in df.groupby(by=["dialogId_x","user_x"]):
        counter[gr[0]] += sum(gr[1]["prediction"])

    return [x[0] for x in counter.most_common(len(counter))]


def order_to_scores(pairs):
    records = []
    for i, (d, u) in enumerate(pairs):
        records.append((d, u, -i))

    return pd.DataFrame.from_records(records, columns=["dialogId", "user", "prediction"])


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--features', type=str, required=True)
    parser.add_argument('-m', '--model', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    args = parser.parse_args()

    bst = xgb.Booster()
    bst.load_model(args.model)

    df = pd.DataFrame.from_csv(args.features).reset_index()
    bin_df = reg_to_binary(df)

    order = to_order(bin_df, bst)
    res = order_to_scores(order)
    mg = pd.merge(res, df, on=["dialogId", "user"])

    submit = df_to_submit(mg)
    submit.to_csv(args.output, header=False, index=False)