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


if __name__ == '__main__':

    data_files = [
        # 'datasets/turing-data/test_20170724.json',
        # 'datasets/turing-data/test_20170725.json',
        # 'datasets/turing-data/test_20170726.json',
        'datasets/turing-data/test_20170727.json',
    ]

    our_zero = -10000

      
    # test_file = "datasets/turing-data/test_20170727.json"
    refineable_file = "submit_q_minus.csv"
    # refineable_file = "lesha_submit.csv"
    submit_file = "hbo_v2.csv"
    # submit_file = "all.csv"

    data = []
    for test_file in data_files:
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

        # if d.bobs[0][1].startswith(" "):
        #     d.alice_q = max(d.alice_q, -380)
        #     d.bob_q = -1000
        #     continue

        # else:
        #     d.alice_q = -380
        #     d.bob_q = -1000
        # continue

        # if len(d.alices) == -1000 and len(d.bobs) > -1000:
        #     if d.bobs[0][1].startswith(" "):
        #         d.alice_q = -1000
        #         d.bob_q = -380
        #     else:
        #         d.alice_q = -380
        #         d.bob_q = -1000
        #     continue

        

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

        # if d.alice_q < -380 and d.bob_q < -380:
        #     if d.alice_q < d.bob_q:
        #         d.alice_q = -1000
        #         d.bob_q = -380
        #     else:
        #         d.alice_q = -380
        #         d.bob_q = -1000
        #     continue

        # if d.alice_q == -1000 and d.bob_q < -380:
        #     d.bob_q = -1000
        # if d.alice_q < -380 and d.bob_q == -1000:
        #     d.alice_q = -1000

        # if len(d.alices) == -1000 and len(d.bobs) == -1000:
        #     d.alice_q = -1000
        #     d.bob_q = -380
        
    
    # for i, d in enumerate(data):
        
    #     if d.alice_q > 1:
    #         d.alice_q = min(4.0, d.alice_q+0.75)
    #     if d.bob_q > 1:
    #         d.bob_q = min(4.0, d.bob_q+0.75)




    with open(submit_file, "w") as fh:
        for i, d in enumerate(data):
            fh.write("%s,%s,%s\n" % (d.id, d.alice_q, d.bob_q))










