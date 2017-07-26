#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@author: Aleksey Komissarov
#@contact: ad3002@gmail.com 

import simplejson
from sklearn.metrics import roc_auc_score
from collections import Counter
from scipy.stats import spearmanr

def get_bots(file_name):
    
    file_name = file_name

    pos = 0
    neg = 0
    result= ""
    
    p1 = 0
    p2 = 0

    p_for_one = 1.0
    p_for_zero = 0.0

    y_true = []
    y_pred = []
    errors = 0

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
        y_pred.append(1)
        if users["bob"] == "Human":
            y_true.append(p_for_one)
        else:
            y_true.append(p_for_zero)
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
            y_pred[-2] = 0.0
            y_pred[-1] = 1.0
        if bob_txt.strip() == "":
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

        # if abs(y_pred[-1] - y_true[-1]) > 0.1 or abs(y_pred[-2] - y_true[-2]) > 0.1:
        #     if y_pred[-1] == y_pred[-2] == 0.5:
        #         continue
        #     print "="*30
        #     print "alice", users["alice"], alice, y_pred[-2], y_true[-2]
        #     print "bob", users["bob"], bob, y_pred[-1], y_true[-1]     
        #     # raw_input("?")       
        #     errors += 1

    print len(y_true), "errors:", errors, "ROC AUC", roc_auc_score(y_true, y_pred)
    return y_pred

def value(x,y):
    if x == 0:
        return x
    return y

if __name__ == '__main__':
    
    file_name = "train4.json"

    bots = get_bots(file_name)

    print bots

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
    true_bots = []

    cnn_generated_data = []

    with open(file_name) as fh:
        data = simplejson.load(fh)
    for did, x in enumerate(data):
        alice = []
        bob = []        
        users = {}
        users_bot = {}
        for r in x["evaluation"]:
            if r["userId"] == "Alice":
                users["alice"] = r["quality"]
            else:
                users["bob"] = r["quality"]

        for r in x["users"]:
            if r["id"] == "Alice":
                users_bot["alice"] = r["userType"]
            else:
                users_bot["bob"] = r["userType"]

        true_bots.append(users_bot["alice"])
        true_bots.append(users_bot["bob"])

        y_true.append(users["alice"])
        y_true.append(users["bob"])
        
        if bots[len(y_true)-2] <= 0.5:
            y_pred.append(0)
        else:
            y_pred.append(2)

        if bots[len(y_true)-1] <= 0.5:
            y_pred.append(0)
        else:
            y_pred.append(2)

        for rid, r in enumerate(x["thread"]):
            if r["userId"] == "Alice":
                alice.append((rid, r["text"]))
            else:
                bob.append((rid,  r["text"]))


        alice_txt = " ".join(["_%s_ %s" % (_x[0],_x[1]) for _x in alice])
        bob_txt = " ".join(["_%s_ %s" % (_x[0],_x[1]) for _x in bob])   

        alice_tokens = set(alice_txt.split())
        bob_tokens = set(bob_txt.split())

        if len(alice) + len(bob) < 5:
            y_pred[-1] = value(y_pred[-1], 1)
            y_pred[-2] = value(y_pred[-2], 1)
        else:
            y_pred[-1] = value(y_pred[-1], y_pred[-1]+1)
            y_pred[-2] = value(y_pred[-2], y_pred[-1]+1)
        if len(alice) + len(bob) > 20:
            y_pred[-1] = value(y_pred[-1], y_pred[-1]+1)
            y_pred[-2] = value(y_pred[-2], y_pred[-1]+1)
        if len(alice) + len(bob) > 40:
            y_pred[-1] = value(y_pred[-1], y_pred[-1]+1)
            y_pred[-2] = value(y_pred[-2], y_pred[-1]+1)


        cnn_generated_data.append({
                "product": str(y_true[-2]),
                "consumer_complaint_narrative": alice_txt
            })
        cnn_generated_data.append({
                "product": str(y_true[-1]),
                "consumer_complaint_narrative": bob_txt
            })


        # if alice_txt.strip() == "":
        #     y_pred[-2] = value(y_pred[-2], 1)
        # if bob_txt.strip() == "":
        #     y_pred[-1] = value(y_pred[-1], 1)
        # if alice_txt.strip() == "" and bob_txt.strip() == "":
        #     y_pred[-1] = value(y_pred[-1], 1)
        #     y_pred[-2] = value(y_pred[-2], 1)

        # if alice_txt.strip() == "" and isinstance(bob_txt, unicode):
        #     y_pred[-1] = 1.0
        #     y_pred[-2] = 0.0
        # if bob_txt.strip() == "" and isinstance(alice_txt, unicode):
        #     y_pred[-1] = 0.0
        #     y_pred[-2] = 1.0            

        # if len([x[1] for x in alice]) > len(set([x[1] for x in alice])):
        #     y_pred[-2] = value(y_pred[-2], 1)
        #     y_pred[-1] = value(y_pred[-1], 1)
        # if len([x[1] for x in bob]) > len(set([x[1] for x in bob])):
        #     y_pred[-2] = value(y_pred[-2], 1)
        #     y_pred[-1] = value(y_pred[-1], 1)

        # if len([x[1] for x in bob]) > len(set([x[1] for x in bob])) and len([x[1] for x in alice]) > len(set([x[1] for x in alice])):
        #     y_pred[-2] = value(y_pred[-2], 3)
        #     y_pred[-1] = value(y_pred[-1], 3)

        # if (0, "avilable") in bob:
        #     y_pred[-1] = value(y_pred[-1], 1)
        # if (0, "avilable") in alice:
        #     y_pred[-2] = value(y_pred[-2], 1)    

        # if "Hint: first" in alice_txt:
        #     y_pred[-1] = value(y_pred[-1], 1)
        #     y_pred[-2] = value(y_pred[-2], 1)                
        # if "Hint: first" in bob_txt:
        #     y_pred[-1] = value(y_pred[-1], 1)
        #     y_pred[-2] = value(y_pred[-2], 1)                

        # if " ." in alice_txt or " ," in alice_txt:
        #     y_pred[-1] = 1.0
        #     y_pred[-2] = 0.0
        # if " ." in bob_txt or " ," in bob_txt:
        #     y_pred[-1] = 0.0
        #     y_pred[-2] = 1.0  


        # if "\n" in alice_txt:
        #     y_pred[-1] = 1.0
        #     y_pred[-2] = 0.0
        # if "\n" in bob_txt:
        #     y_pred[-1] = 0.0
        #     y_pred[-2] = 1.0  


        # if users["bob"] == 1 and users["alice"] == 1:
        #     print "=============="
        #     print alice_txt
        #     print bob_txt

        if y_true[-2] != y_pred[-2]:
            print did, y_true[-2], y_pred[-2], true_bots[-2], bots[len(y_true)-2]
            print alice_txt
        if y_true[-1] != y_pred[-1]:
            print did, y_true[-1], y_pred[-1], true_bots[-1], bots[len(y_true)-1]
            print bob_txt

        s = "%s,%s,%s\n" % (x["dialogId"], y_pred[-2], y_pred[-1])
        result += s

    with open("answer_day2_alice_bob.csv", "w") as fh:
        fh.write(result)    


    print Counter(y_true)
    errors = 0
    for i,x in enumerate(y_true):
        if x == y_pred[i]:
            continue
        errors += 1
        # print i, x, y_pred[i], true_bots[i], bots[i]
    # print y_true
    # print y_pred

    print spearmanr(y_true, y_pred)

    y_true_nobot = []
    y_pred_nobot = []
    for i,x in enumerate(y_true):
        if x == 0:
            continue
        y_true_nobot.append(x)
        y_pred_nobot.append(y_pred[i])

    print spearmanr(y_true_nobot, y_pred_nobot)
    print "Errors", errors, len(y_true)/2

    with open("cnn_data.json", "w") as fh:
        simplejson.dump(cnn_generated_data, fh)






