#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@author: Aleksey Komissarov
#@contact: ad3002@gmail.com 

import simplejson

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


def refine(refineable_file, submit_file, test_files):
    data = []
    for test_file in test_files:
        with open(test_file) as fh:
            data += [DialogTest(x) for x in simplejson.load(fh)]
    

    our_zero = -10000


    data = []
    for test_file in test_files:
        with open(test_file) as fh:
            data += [DialogTest(x) for x in simplejson.load(fh)]

    with open(refineable_file) as fh:
        M = {}
        for line in fh:
            if line.startswith("#"):
                continue
            if line.startswith("dialogId"):
                continue
            d = line.strip().split(",")
            M[int(d[0])] = (float(d[1]),float(d[2]))
    for i, d in enumerate(data):
        data[i].alice_q = round(M[d.id][0],3)
        data[i].bob_q = round(M[d.id][1],3)

    for i, d in enumerate(data):

        # alice_spaces = len([x for x in d.alices if x[1].startswith(" ")])
        # if alice_spaces > 0:
        #     d.alice_q = max(d.alice_q, -380)
        #     d.bob_q = our_zero
        #     continue

        # bob_spaces = len([x for x in d.bobs if x[1].startswith(" ")])
        # if bob_spaces > 0:
        #     d.bob_q = max(d.bob_q, -380)
        #     d.alice_q = our_zero
        #     continue

        if d.alice_q < our_zero:
            d.alice_q = our_zero
        if d.bob_q < our_zero:
            d.bob_q = our_zero

        if d.alices and d.alices[0][1].startswith("wtf"):
            d.alice_q = max(d.alice_q, -380)
            d.bob_q = our_zero
            continue
         
        if d.bobs and d.bobs[0][1].startswith("wtf"):
            d.bob_q = max(d.bob_q, -380)
            d.alice_q = our_zero
            continue
         
        if d.alices and d.alices[0][1].startswith(" "):
            d.alice_q = max(d.alice_q, -380)
            d.bob_q = our_zero
            continue

        if d.bobs and d.bobs[0][1].startswith(" "):
            d.bob_q = max(d.bob_q, -380)
            d.alice_q = our_zero
            continue


        bot_marksers = [
            "Interesting fact",
            "Answer, amaze and amuse.",
            "I can answer your questions. Ask me anything!",
            # "\n",
            # " .",
            " ,",
            # " \'",
            " 's",
            "<",
            "/end",
            "/start",
            "Talking is the best.",
            "I will ask you a question in a second, please wait.",
            "Congressional",
            "I don't understand what's",
        ]

        for x in bot_marksers:
            if x in d.alice_txt:
                d.alice_q = max(d.alice_q, -380)
                d.bob_q = our_zero
                break
            if x in d.bob_txt:
                d.bob_q = max(d.bob_q, -380)
                d.alice_q = our_zero
                break


    with open(submit_file, "w") as fh:
        for i, d in enumerate(data):
            fh.write("%s,%s,%s\n" % (d.id, d.alice_q, d.bob_q))


if __name__ == '__main__':


    test_files = [
        # 'datasets/turing-data/test_20170724.json',
        # 'datasets/turing-data/test_20170725.json',
        # 'datasets/turing-data/test_20170726.json',
        'datasets/turing-data/test_20170727.json',
    ]

    refineable_file = "submit_q_minus.csv"
    # refineable_file = "all_hbo.csv"
    # refineable_file = "lesha_submit.csv"
    # submit_file = "all_hbo_refined.csv"
    submit_file = "all.csv"
    submit_file = "hbo_v2.csv"

    refine(refineable_file, submit_file, test_files)


    # parser = argparse.ArgumentParser()
    # parser.add_argument('-d', '--dialogs', type=str, required=True)
    # parser.add_argument('-i', '--input', type=str, required=True)
    # parser.add_argument('-o', '--output', type=str, required=True)
    # args = parser.parse_args()
    # refine(args.input, args.output, [args.dialogs])










