#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import pickle

import util.cfg
util.cfg.default = {"order": 2, "randomWalk": True}

context = [-1,] * 5
phrases = []
phraseList = {}
mots = {}
cfg = util.cfg.default

def initDb():
    """Loads the DB"""
    global phrases, phraseList, mots, cfg

    cfg = util.cfg.load("markov.json")

    if os.path.isfile("phrases"):
        with open("phrases", "rb") as f:
            phrases = pickle.load(f)
    
    if os.path.isfile("nodes-phrases"):
        with open("nodes-phrases", "rb") as f:
            phraseList = pickle.load(f)
    
    if os.path.isfile("mots"):
        with open("mots", "rb") as f:
            mots = pickle.load(f)

def computeRandomSentence():
    """Computes a random sentence"""
    starts = [i for i in mots.keys() if i[0:4]=="END|"]
    
    ph = starts[random.randint(0,len(starts)-1)]
    
    while ph[-4:]!="|END":
        lst = mots["|".join(ph.split("|")[-cfg["order"]:])]
        if cfg["randomWalk"]:
            ph += "|" + list(lst.keys())[random.randint(0, len(lst)-1)]
        else:
            total = sum([lst[i] for i in lst.keys()])
            baseValue = 0
            value = random.randint(0, total-1)
            for candidat in lst.keys():
                if baseValue <= value and lst[candidat] > value:
                    ph += "|" + candidat
                    break
                baseValue += lst[candidat]
    
    return " ".join(ph.split("|")[1:-1])

def AnalyzeSentence(phrase):
    """Analyzes a sentence"""
    global mots
    
    p = ["END",] + phrase.split() + ["END",]
    
    for i in range(len(p)-cfg["order"]):
        node = "|".join(p[i:i+cfg["order"]])
        if mots.__contains__(node):
            if mots[node].__contains__(p[i+cfg["order"]]):
                mots[node][p[i+cfg["order"]]] += 1
            else:
                mots[node][p[i+cfg["order"]]] = 1
        else:
            mots[node] = {p[i+cfg["order"]]: 1}
    
    with open("mots", "wb") as f:
        pickle.dump(mots, f)

def AnalyseFile(filename):
    """Analyzes a file"""
    text = open(filename, "r")
    global context, phrases, phraseList, mots, context
    
    for lineId, phrase in enumerate(text.readlines()):
        print("Analyzing line %d..." % lineId, end="\x1B[0K\r")
        
        phrase = phrase.replace("\n", "")
        
        # Analyse de chaque mot d'une phrase, et de leur relation
        p = ["END",] + phrase.split() + ["END",]
        
        for i in range(len(p)-cfg["order"]):
            node = "|".join(p[i:i+cfg["order"]])
            if mots.__contains__(node):
                if mots[node].__contains__(p[i+cfg["order"]]):
                    mots[node][p[i+cfg["order"]]] += 1
                else:
                    mots[node][p[i+cfg["order"]]] = 1
            else:
                mots[node] = {p[i+cfg["order"]]: 1}
        
        # Analyse de chaque phrase, et de leurs relation
        if not phrases.__contains__(phrase):
            phrases.append(phrase)
        
        idx = phrases.index(phrase)
        context = context[1:] + [idx,]
        for i in range(5):
            c = "%d|%d|%d|%d|%d" % tuple(([-1,]*5)[0:i] + context[i:5])
            
            if c != "-1|-1|-1|-1|-1":
                if phraseList.__contains__(c):
                    if phraseList[c].__contains__(idx):
                        phraseList[c][idx] += 1
                    else:
                        phraseList[c][idx] = 1
                else:
                    phraseList[c] = {idx:1}
    
    with open("mots", "wb") as f:
        pickle.dump(mots, f)
    
    with open("nodes-phrases", "wb") as f:
        pickle.dump(phraseList, f)
    
    with open("phrases", "wb") as f:
        pickle.dump(phrases, f)
    
    text.close()

def compute(item):
    """Computes an answer to a given sentence, taking into account the current context"""
    global context, phrases, phraseList
    
    answer = ""
    AnalyzeSentence(item)

    if not phrases.__contains__(item):
        phrases.append(item)
        with open("phrases", "wb") as f:
            pickle.dump(phrases, f)
    
    idx = phrases.index(item)
    context = context[1:] + [idx,]

    found = False
    for i in range(5):
        c = "%d|%d|%d|%d|%d" % tuple(([-1,] * 5)[0:i] + context[i:5])

        if phraseList.__contains__(c):
            found = True
            if phraseList[c].__contains__(idx):
                phraseList[c][idx] += 1
            else:
                phraseList[c][idx] = 1
            
            lst = list(phraseList[c].keys())
            idx = phraseList[c][lst[random.randint(0, len(lst)-1)]]
            answer = phrases[idx]
            context = context[1:] + [idx,]

            foundRep = False
            for j in range(5):
                c = "%d|%d|%d|%d|%d" % tuple(([-1,]*5)[0:j] + context[j:5])
                if phraseList.__contains__(c):
                    foundRep = True
                    if phraseList[c].__contains__(idx):
                        phraseList[c][idx] += 1
                    else:
                        phraseList[c][idx] = 1
                    break

            if not foundRep:
                for j in range(5):
                    c = "%d|%d|%d|%d|%d" % tuple(([-1,]*5)[0:j] + context[j:5])
                    phraseList[c] = {idx:1}
                with open("nodes-phrases", "wb") as f:
                    pickle.dump(phraseList, f)
                break

    if not found:
        item = computeRandomSentence()
        if not phrases.__contains__(item):
            phrases.append(item)
            with open("phrases", "wb") as f:
                pickle.dump(phrases, f)

        idx = phrases.index(item)
        answer = item
        context = context[1:] + [idx,]

        foundRep = False
        for i in range(5):
            c = "%d|%d|%d|%d|%d" % tuple(([-1,]*5)[0:i] + context[i:5])
            if phraseList.__contains__(c):
                foundRep = True
                if phraseList[c].__contains__(idx):
                    phraseList[c][idx] += 1
                else:
                    phraseList[c][idx] = 1
                break

        if not foundRep:
            for i in range(5):
                c = "%d|%d|%d|%d|%d" % tuple(([-1,]*5)[0:i] + context[i:5])
                phraseList[c] = {idx:1}
            with open("nodes-phrases", "wb") as f:
                pickle.dump(phraseList, f)

    return answer

def dumpGraph(filePath):
    """Dump graph to a file"""
    graphFile = open(filePath, "w")
    graphFile.write("digraph G {\n")
    for key in mots.keys():
        for item in mots[key]:
            left = " ".join(key.replace("\\", "\\\\").replace('"', '\\"').split("|"))
            right = (" ".join((key+"|" + item).split("|")[-cfg["order"]:])).replace("\\", "\\\\").replace('"', '\\"')
            if left[0:4] == "END ":
                graphFile.write('\t"%s" [color="#3faf3f", style=filled];\n' % left)

            if right[-4:] == " END":
                graphFile.write('\t"%s" [color="#af3f3f", style=filled];\n' % right)

            graphFile.write('\t"%s" -> "%s" [label="%d"];\n' % (left, right, mots[key][item]))

    graphFile.write("}\n")
    graphFile.close()
