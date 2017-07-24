import xgboost as xgb
import pandas as pd
import logging
import argparse

logger = logging.getLogger(__name__)


def run(model_path, features_path, outpath):
    logger.info("loading model")
    bst = xgb.Booster()
    bst.load_model(model_path)

    logger.info("loading features")
    feats = pd.DataFrame.from_csv(features_path)
    dtest = xgb.DMatrix(feats.values)
    logger.info("predicting")
    preds = bst.predict(dtest)

    feats["human-generated"] = preds
    result = feats["human-generated"]

    result.index.name = "id"

    logger.info("dumping")
    result.to_csv(outpath, header=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, required=True)
    parser.add_argument('-f', '--features', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)

    args = parser.parse_args()

    run(args.model, args.features, args.output)

