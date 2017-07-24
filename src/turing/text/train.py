import xgboost as xgb
import pandas as pd
import os
from sklearn.metrics import roc_auc_score, roc_curve
from collections import Counter
import pickle
import logging
import argparse

logger = logging.getLogger(__name__)

def run(input_features, input_evals, input_labels, prev_model, outpath):
    logger.info("starting reading")
    train = pd.DataFrame.from_csv(input_features)
    evals = pd.DataFrame.from_csv(input_evals)
    labels = pd.DataFrame.from_csv(input_labels, sep='\t')

    train["label"] = labels["human-generated"]
    evals["label"] = labels["human-generated"]

    label_column = train["label"]
    label_column_eval = evals["label"]

    features = train.drop(["label"], axis=1)
    features_evals = evals.drop(["label"], axis=1)

    logger.info("constructing matrix")
    dtrain = xgb.DMatrix(features.values, label_column.values)
    deval = xgb.DMatrix(features_evals.values, label_column_eval.values)

    param = {'eta': 0.1, 'max_depth': 6, 'min_child_weight': 2, 'gamma': 0.1,
             'silent': 0, 'subsample': 0.9, 'colsample_bytree': 0.6,
             'reg_alpha':100, 'reg_lambda': 0.1,
             'objective': 'binary:logistic', 'eval_metric': 'auc'}

    logger.info("actual training {}".format(dtrain.num_row()))
    bst = xgb.train(param, dtrain, evals=[(deval,"ev1")], num_boost_round=500,
                    early_stopping_rounds=20, xgb_model=prev_model)

    logger.info("dumping into {}".format(outpath))
    bst.save_model(outpath)
    logger.info("success")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--features', type=str, required=True)
    parser.add_argument('-e', '--evals', type=str, required=True)
    parser.add_argument('-l', '--labels', type=str, required=True)
    parser.add_argument('-m', '--model', type=str, default=None)
    parser.add_argument('-o', '--output', type=str, required=True)

    args = parser.parse_args()

    run(args.features, args.evals, args.labels, args.model, args.output)
