import re

import pandas as pd
import numpy as np
import scipy.sparse as sp

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, roc_curve
from xgboost.sklearn import XGBClassifier
import logging

first_second = re.compile(r'<first_speaker>(.*?)<second_speaker>', re.IGNORECASE)
first_second = re.compile(r'<first_speaker>(.*?)<second_speaker>', re.IGNORECASE)


def add_features(df, X):
    context_has_first = df.context.apply(lambda x: x.count('first_speaker'))
    context_has_second = df.context.apply(lambda x: x.count('second_speaker'))
    context_has_third = df.context.apply(lambda x: x.count('third_speaker'))

    response_has_first = df.response.apply(lambda x: x.count('first_speaker'))
    response_has_second = df.response.apply(lambda x: x.count('second_speaker'))
    response_has_third = df.response.apply(lambda x: x.count('third_speaker'))
    
    response_len = df.response.apply(lambda x: len(x))
    context_len = df.context.apply(lambda x: len(x))
    
    dogs_count_response = df.response.apply(lambda x: x.count('@'))
    dogs_count_context = df.context.apply(lambda x: x.count('@'))

    at_count_response = df.response.apply(lambda x: x.count('<at>'))
    at_count_context = df.context.apply(lambda x: x.count('<at>'))

    url_count_response = df.response.apply(lambda x: x.count('<url>'))
    url_count_context = df.context.apply(lambda x: x.count('<url>'))

    context_words = df.context.apply(lambda x: len(x.replace('@@ ', '').split()) * 1.0)
    context_chars = df.context.apply(lambda x: len(x.replace('@@ ', '')) * 1.0)
    context_avg_word_len = pd.Series(np.divide(context_chars, context_words))

    response_words = df.response.apply(lambda x: len(x.replace('@@ ', '').split()) * 1.0)
    response_chars = df.response.apply(lambda x: len(x.replace('@@ ', '')) * 1.0)
    response_avg_word_len = pd.Series(np.divide(response_chars, response_words))

    context_speakers_count = ((context_has_first > 0) * 1.0 +
                              (context_has_second > 0) * 1.0 +
                              (context_has_third > 0) * 1.0)

    response_speakers_count = ((response_has_first > 0) * 1.0 +
                               (response_has_second > 0) * 1.0 +
                               (response_has_third > 0) * 1.0)

    context_r_count = context_has_first + context_has_second + context_has_third
    response_r_count = response_has_first + response_has_second + response_has_third

    np_context_has_first = context_has_first.values
    np_response_has_first = response_has_first.values
    np_context_has_second = context_has_second.values
    np_response_has_second = response_has_second.values
    np_context_has_third = context_has_third.values
    np_response_has_third = response_has_third.values

    c1 = ((np_context_has_first > 0) & (np_response_has_first > 0) &
          (np_context_has_second == 0) & (np_response_has_second == 0) &
          (np_context_has_third == 0) & (np_response_has_third == 0))

    c2 = ((np_context_has_first == 0) & (np_response_has_first == 0) &
          (np_context_has_second > 0) & (np_response_has_second > 0) &
          (np_context_has_third == 0) & (np_response_has_third == 0))

    c3 = ((np_context_has_first == 0) & (np_response_has_first == 0) &
          (np_context_has_second == 0) & (np_response_has_second == 0) &
          (np_context_has_third > 0) & (np_response_has_third > 0))

    context_response_same = pd.Series(c1 | c2 | c3)

    cols = [context_has_first, context_has_second, context_has_third, response_has_first,
            response_has_second, response_has_third, response_len, context_len,
            dogs_count_response, dogs_count_context, response_words, response_chars,
            response_avg_word_len, context_speakers_count, response_speakers_count, context_r_count,
            response_r_count, context_response_same, context_words, context_chars, context_avg_word_len,
            at_count_response, at_count_context, url_count_context, url_count_response]

    return sp.hstack([X] + [m.values[:, None] for m in cols])


def train_xgb_search(df_train, df_validate, df_test):
    cv = CountVectorizer(token_pattern=r'\S+', ngram_range=(1, 3), min_df=10, binary=True, dtype=np.uint8)
    
    print('fit & transform')
    X_train = cv.fit_transform(df_train.response)
    print('add features')
    X_train = add_features(df_train, X_train)
    
    y_train = df_train['human-generated'].values
    
    X_validate = cv.transform(df_validate.response)
    X_validate = add_features(df_validate, X_validate)
    y_validate = df_validate['human-generated'].values
    
    for d in [9]:
        for lr in [0.3]:
            for ne in [200]:
                xgb = XGBClassifier(max_depth=d, learning_rate=lr, n_estimators=ne, nthread=40)
                xgb.fit(X_train, y_train)
                y_pred = xgb.predict_proba(X_validate)
                score = roc_auc_score(y_validate, y_pred[:, 1])
                print("max_depth={}, learning_rate={}, n_estimators={}: {}".format(d, lr, ne, score))


def train_xgb(df_train, df_validate, df_test):
    
    print('test submit')
    cv = CountVectorizer(token_pattern=r'\S+', ngram_range=(1, 3), min_df=10, binary=True, dtype=np.uint8)
    df_all = pd.concat((df_train, df_validate))
    
    print('fit & transform')
    X_train = cv.fit_transform(df_all.response)
    X_train = add_features(df_all, X_train)
    y_train = df_all['human-generated'].values
    
    print('fit')
    xgb = XGBClassifier(max_depth=15, learning_rate=0.3, n_estimators=60, nthread=40)
    xgb.fit(X_train, y_train)
    
    X_test = cv.transform(df_test.response)
    X_test = add_features(df_test, X_test)
    y_pred = xgb.predict_proba(X_test)
    df_res = pd.DataFrame()
    df_res['id'] = df_test.id
    df_res['human-generated'] = y_pred[:, 1]

    df_res.to_csv('sub_xgb_features_2.csv', index=False)
    
    return True


if __name__ == '__main__':
    train = pd.read_csv('data/train.txt', sep='\t')
    validate = pd.read_csv('data/validation.txt', sep='\t')
    test = pd.read_csv('data/test.txt', sep='\t')

    print(train_xgb_search(train, validate, test))

    #y_pred = train_c2(df_train, df_validate, df_test)
    #import joblib
    #joblib.dump(y_pred, 'y_pred.joblib')
    #joblib.dump(df_test.id, 'id.joblib')
    #df_res = pd.DataFrame()
    #df_res['id'] = df_test.id
    #df_res['human-generated'] = y_pred

    #df_res.to_csv('sub2.csv', index=False)
