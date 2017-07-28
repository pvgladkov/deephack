import argparse
import pandas as pd
import json


def flatten_dialogs(diags):
    res = []
    for d in diags:
        for t in d["thread"]:
            if len(t["text"].strip(" *")) > 10 and "\n" not in t["text"]:
                res.append((d["dialogId"], t["userId"], t["text"].encode("utf-8")))

    return pd.DataFrame.from_records(res, columns=["dialogId", "userId", "text"])


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dialogs', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-t', '--tmp_output', type=str, required=True)


    args = parser.parse_args()

    diags = json.load(open(args.dialogs))
    df = flatten_dialogs(diags)

    df.to_csv(args.output, index=False)
    df["text"].to_csv(args.tmp_output, index=False)