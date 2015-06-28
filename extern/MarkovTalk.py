#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import pickle

import util.cfg
util.cfg.default = {"order": 2, "randomWalk": True}

mots = {}
lastNode = ""
cfg = util.cfg.default

def initDb():
    """Loads the DB"""
    global mots, cfg

    cfg = util.cfg.load("markov.json")

    if os.path.isfile("mots"):
        with open("mots", "rb") as f:
            mots = pickle.load(f)

def computeRandomSentence(startFromLast=False):
    """Computes a random sentence"""
    global lastNode

    # Decides which node to start from
    if startFromLast and lastNode!="" and mots.__contains__(lastNode) and len(mots[lastNode])>0:
        if cfg["randomWalk"] == True:
            lst = list(mots[lastNode].keys())
            ph = lst[random.randint(0, len(lst)-1)]
        else:
            total = sum([mots[lastNode][i] for i in mots[lastNode].keys()])
            baseValue = 0
            value = random.randint(0, total - 1)
            for candidat in mots[lastNode].keys():
                if baseValue <= value and mots[lastNode][candidat] > value:
                    ph = candidat
                    break
                baseValue += mots[lastNode][candidat]

    else:
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

    lastNode="|".join(ph.split("|")[-cfg["order"]:])
    
    return " ".join(ph.split("|")[1:-1])

def AnalyzeSentence(phrase):
    """Analyzes a sentence"""
    global mots, lastNode
    
    p = ["END",] + phrase.split() + ["END",]
   
    # Analyze each group of words
    for i in range(len(p)-cfg["order"]):
        node = "|".join(p[i:i+cfg["order"]])
        if mots.__contains__(node):
            if mots[node].__contains__(p[i+cfg["order"]]):
                mots[node][p[i+cfg["order"]]] += 1
            else:
                mots[node][p[i+cfg["order"]]] = 1
        else:
            mots[node] = {p[i+cfg["order"]]: 1}

    # Update lastNode stats to reflect lastNode -> current sentence link weight
    if mots.__contains__(lastNode):
        if mots[lastNode].__contains__(p[0:cfg["order"]]):
            mots[lastNode][p[0:cfg["order"]]] += 1
        else:
            mots[lastNode][p[0:cfg["order"]]] = 1
    else:
        mots[lastNode] = {p[0:cfg["order"]]: 1}

    # Update lastNode to what the user just said
    lastNode = "|".join(p[-cfg["order"]:])
    
    with open("mots", "wb") as f:
        pickle.dump(mots, f)

def AnalyseFile(filename):
    """Analyzes a file"""
    text = open(filename, "r")
    global mots, lastNode
    
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
    
        if mots.__contains__(lastNode):
            if mots[lastNode].__contains__(p[0:cfg["order"]]):
                mots[lastNode][p[0:cfg["order"]] += 1
            else:
                mots[lastNode][p[0:cfg["order"]] = 1
        else:
            mots[lastNode] = {p[0:cfg["order"]]: 1}

        lastNode = "|".join(p[-cfg["order"]:])
        
    with open("mots", "wb") as f:
        pickle.dump(mots, f)
    
    text.close()

def compute(item):
    """Computes an answer to a given sentence, taking into account the lastNode value"""
    AnalyzeSentence(item)
    return computeRandomSentence(True)

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

                # write next node candidates
                if mots.__contains__(item):
                    for nextItem in mots[item]:
                        graphFile.write('\t"%s" -> "%s" [color="#7f7f7f"]\n' % (right, (" ".join(nextItem.split("|")))).replace("\\", "\\\\").replace('"', '\\"'))


            graphFile.write('\t"%s" -> "%s" [label="%d"];\n' % (left, right, mots[key][item]))

    graphFile.write("}\n")
    graphFile.close()
