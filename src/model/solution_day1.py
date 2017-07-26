#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@author: Aleksey Komissarov
#@contact: ad3002@gmail.com 

import simplejson
from sklearn.metrics import roc_auc_score


def get_bots():
    
    file_name = "data3.txt"

    pos = 0
    neg = 0
    result= ""
    
    p1 = 0
    p2 = 0

    p_for_one = 1.0
    p_for_zero = 0.0

    y_true = []
    y_pred_dict = {}
    y_pred = []
    errors = 0

    with open("baseline.txt") as fh:
        fh.readline()
        data = [x.strip().split(",") for x in fh]
    for x in data:
        pa = float(x[2])
        pb = float(x[3])

        if pa == 0.5:
            pa = 1.0
        if pb == 0.5:
            pb = 1.0

        pa = pb = 1.0

        # if pa > pb:
        #     pa = pb
        y_pred_dict[int(x[1])] = (pa, pb)

    # with open("answer.tsv") as fh:
    #     # fh.readline()
    #     data = [x.strip().split(",") for x in fh]
    # for x in data:
    #     y_pred_dict[int(x[0])] = (float(x[1]), float(x[2]))
    #     y_pred_dict[int(x[0])] = (0.7, 0.8)


    with open(file_name) as fh:
        data = simplejson.load(fh)
    for x in data:
        alice = []
        bob = []        
        users = {}
        for r in x["users"]:
            if r["id"] == "Alice":
                users["alice"] = r["userType"]
            else:
                users["bob"] = r["userType"]

        if users["alice"] == "Human":
            y_true.append(p_for_one)
        else:
            y_true.append(p_for_zero)
        # y_pred.append(y_pred_dict[x["dialogId"]][0])
        y_pred.append(1)
        if users["bob"] == "Human":
            y_true.append(p_for_one)
        else:
            y_true.append(p_for_zero)
      
        # y_pred.append(y_pred_dict[x["dialogId"]][1])
        y_pred.append(1)
        
        for rid, r in enumerate(x["thread"]):
            if r["userId"] == "Alice":
                alice.append((rid, r["text"]))
            else:
                bob.append((rid,  r["text"]))

        s = "%s,%s,%s\n" % (x["dialogId"], p1, p2)
        result += s

        alice_txt = " ".join(["_%s_ %s" % (x[0],x[1]) for x in alice])
        bob_txt = " ".join(["_%s_ %s" % (x[0],x[1]) for x in bob])

        if alice_txt.strip() == "":
            # print "HIT"

            # print users["alice"], alice
            # print users["bob"], bob        
            # raw_input("?")
            y_pred[-2] = 0.0
            y_pred[-1] = 1.0
        if bob_txt.strip() == "":
            # print "HIT"
            
            # print users["alice"], alice
            # print users["bob"], bob        
            # raw_input("?")
            y_pred[-1] = 0.0
            y_pred[-2] = 1.0

        if alice_txt.strip() == "" and bob_txt.strip() == "":
            y_pred[-1] = 0.5
            y_pred[-2] = 0.5

        if alice_txt.strip() == "" and isinstance(bob_txt, unicode):
            y_pred[-2] = 0.3
            y_pred[-1] = 1.0
        if bob_txt.strip() == "" and isinstance(alice_txt, unicode):
            y_pred[-1] = 0.3
            y_pred[-2] = 1.0            

        if len([x[1] for x in alice]) > len(set([x[1] for x in alice])):
            y_pred[-2] = 0.3
            y_pred[-1] = 0.7
        if len([x[1] for x in bob]) > len(set([x[1] for x in bob])):
            y_pred[-1] = 0.3
            y_pred[-2] = 0.7

        if len([x[1] for x in bob]) > len(set([x[1] for x in bob])) and len([x[1] for x in alice]) > len(set([x[1] for x in alice])):
            y_pred[-1] = 0.5
            y_pred[-2] = 0.5

        if (0, "avilable") in bob:
            y_pred[-1] = 0.0
            y_pred[-2] = 1.0
        if (0, "avilable") in alice:
            y_pred[-1] = 1.0
            y_pred[-2] = 0.0            

        if "Hint: first" in alice_txt:
            y_pred[-1] = 1.0
            y_pred[-2] = 0.0
        if "Hint: first" in bob_txt:
            y_pred[-1] = 0.0
            y_pred[-2] = 1.0  

        if " ." in alice_txt or " ," in alice_txt:
            y_pred[-1] = 1.0
            y_pred[-2] = 0.0
        if " ." in bob_txt or " ," in bob_txt:
            y_pred[-1] = 0.0
            y_pred[-2] = 1.0  


        if "\n" in alice_txt:
            y_pred[-1] = 1.0
            y_pred[-2] = 0.0
        if "\n" in bob_txt:
            y_pred[-1] = 0.0
            y_pred[-2] = 1.0  


        # if len(alice) > 20:
        #     y_pred[-2] = 0.0
        # if len(bob) > 20:
        #     y_pred[-1] = 0.0



        # if y_true[-1] == 0.0 and y_pred[-1] > 0.5:
        #     y_pred[-1] = 0
        # if y_true[-2] == 0.0 and y_pred[-2] > 0.5:
        #     y_pred[-2] = 0

        
        if abs(y_pred[-1] - y_true[-1]) > 0.1 or abs(y_pred[-2] - y_true[-2]) > 0.1:
            if y_pred[-1] == y_pred[-2] == 0.5:
                continue
            print "="*30
            print "alice", users["alice"], alice, y_pred[-2], y_true[-2]
            print "bob", users["bob"], bob, y_pred[-1], y_true[-1]     
            # raw_input("?")       
            errors += 1

    with open("answer.tsv", "w") as fh:
        fh.write(result)    

    # print y_true

    print len(y_true), "errors:", errors
    print roc_auc_score(y_true, y_pred)

    return y_pred

if __name__ == '__main__':
    
    get_bots()

