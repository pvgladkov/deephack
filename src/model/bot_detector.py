#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@author: Aleksey Komissarov
#@contact: ad3002@gmail.com 

import simplejson
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr
import random

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Dialog(object):

    def __init__(self, d):
        self.id = d["dialogId"]
        self.context = d["context"]
        for x in d["evaluation"]:
            if x["userId"] == "Bob":
                self.bob_q = x["quality"]
            else:
                self.alice_q = x["quality"]
        for x in d["users"]:
            if x["id"] == "Bob":
                self.bob = x["userType"]
            else:
                self.alice = x["userType"]
        self.bobs = []
        self.alices = []
        self.dialog = []
        for i, x in enumerate(d["thread"]):
            if x["userId"] == "Bob":
                self.bobs.append((i,x["text"]))
                self.dialog.append(("bob", x["text"]))
            else:
                self.alices.append((i,x["text"]))
                self.dialog.append(("alice", x["text"]))

        self.alice_txt = " ".join(["_%s_ %s" % (x[0],x[1]) for x in self.alices])
        self.bob_txt = " ".join(["_%s_ %s" % (x[0],x[1]) for x in self.bobs])

    def __str__(self):
        print self.alice, self.alice_q
        print self.alice_txt
        print self.bob, self.bob_q
        print self.bob_txt
        return ""

class DialogTest(object):

    def __init__(self, d):
        self.id = d["dialogId"]
        self.context = d["context"]
        self.bob_q = 0
        self.alice_q = 0
        self.bob = "Bot"
        self.alice = "Bot"
        self.bobs = []
        self.alices = []
        self.dialog = []
        for i, x in enumerate(d["thread"]):
            if x["userId"] == "Bob":
                self.bobs.append((i,x["text"]))
                self.dialog.append(("bob", x["text"]))
            else:
                self.alices.append((i,x["text"]))
                self.dialog.append(("alice", x["text"]))

        self.alice_txt = " ".join(["_%s_ %s" % (x[0],x[1]) for x in self.alices])
        self.bob_txt = " ".join(["_%s_ %s" % (x[0],x[1]) for x in self.bobs])

    def __str__(self):
        print self.alice, self.alice_q
        print self.alice_txt
        print self.bob, self.bob_q
        print self.bob_txt
        return ""


data_files = [
    # 'datasets/turing-data/train_20170724.json',
    # 'datasets/turing-data/train_20170725.json',
    # 'datasets/turing-data/train_20170726.json',
    # 'datasets/turing-data/test_20170727.json',
    'datasets/turing-data/train_20170727.json',
]

score_file = "submit_v2.csv"
score_file = "t.1"
# score_file = "all.csv"
# score_file = "submit_q_minus.csv"
manual_mode = False
# manual_mode = True
# start  = 606

data = []
for file_name in data_files:
    with open(file_name) as fh:
        if "train" in file_name:
            data += [Dialog(x) for x in simplejson.load(fh)]
        else:
            data += [DialogTest(x) for x in simplejson.load(fh)]

with open(score_file) as fh:
    M = {}
    for line in fh:
        d = line.strip().split(",")
        M[int(d[0])] = (float(d[1]),float(d[2]))
        
# for i, d in enumerate(data):
#     data[i].alice_q = round(M[d.id][0],3)
#     data[i].bob_q = round(M[d.id][1],3)


if manual_mode:
    
    for i, d in enumerate(data):
        if i < start:
            continue
        print "="*100
        print "%s/%s" % (i, len(data))
        print "="*100

        for user, rep in d.dialog:
            if user == "alice":
                print bcolors.BOLD+bcolors.OKGREEN + rep + bcolors.ENDC
            else:
                print bcolors.BOLD+ bcolors.HEADER + rep + bcolors.ENDC

        if abs(d.alice_q - round(M[d.id][0],3)) < 0.3 and abs(d.bob_q - round(M[d.id][1],3)) < 0.3:
            continue

        alice_q = raw_input(bcolors.OKGREEN+"Alice (%s | %s)?" % (d.alice_q, round(M[d.id][0],3)) + bcolors.ENDC) or d.alice_q
        bob_q = raw_input(bcolors.HEADER+"Bob (%s | %s)?" % (d.bob_q, round(M[d.id][1],3)) + bcolors.ENDC) or d.bob_q        
        print "="*100


y_true = []
y_pred = []
for i, d in enumerate(data):
    y_true.append(d.alice_q)
    y_true.append(d.bob_q)
    y_pred.append(M[d.id][0])
    y_pred.append(M[d.id][1])

print spearmanr(y_true, y_pred)


