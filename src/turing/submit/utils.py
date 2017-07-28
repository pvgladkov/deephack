from collections import defaultdict
import pandas as pd


def get_score(diag, user):
    return filter(lambda x: x["userId"] == user, diag["evaluation"])[0]["quality"]


def is_bot(diag, user):
    text = " ".join([x["text"] for x in diag["thread"] if x["userId"] == user])

    if len(text) == 0:
        return False

    if "avilable" in text:
        return True

    if "Hint: first" in text:
        return True

    if " ." in text or " ," in text or " '" in text:
        return True

    if "\n" in text:
        return True

    if ">" in text:
        return True

    return False


def df_to_submit(df):
    scores = defaultdict(dict)
    for i in range(0, len(df)):
        row = df.iloc[i]
        scores[row["dialogId"]][row["user"]] = row["prediction"]

    records = []
    for dialog_id in scores:
        records.append((dialog_id, scores[dialog_id]["Alice"], scores[dialog_id]["Bob"]))

    return pd.DataFrame.from_records(records, columns=["dialogId", "Alice", "Bob"])