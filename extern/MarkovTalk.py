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
    ph = ""

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
                    break
                baseValue += mots[lastNode][candidat]
            ph = candidat
    else:
        return ""
    
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

    curOrder = min(cfg["order"], len(ph.split("|"))-1)
    lastNode="|".join(ph.split("|")[-curOrder:])
    
    return " ".join(ph.split("|")[1:-1])

def AnalyzeSentence(phrase):
    """Analyzes a sentence"""
    global mots, lastNode
    
    p = ["END",] + phrase.split() + ["END",]
    curOrder = min(cfg["order"],len(p)-1)

    # Analyze each group of words
    for i in range(len(p)-curOrder):
        node = "|".join(p[i:i+curOrder])
        if mots.__contains__(node):
            if mots[node].__contains__(p[i+curOrder]):
                mots[node][p[i+curOrder]] += 1
            else:
                mots[node][p[i+curOrder]] = 1
        else:
            mots[node] = {p[i+curOrder]: 1}

    # Update lastNode stats to reflect lastNode -> current sentence link weight
    if len(lastNode)>0:
        if mots.__contains__(lastNode):
            if mots[lastNode].__contains__("|".join(p[0:curOrder])):
                mots[lastNode]["|".join(p[0:curOrder])] += 1
            else:
                mots[lastNode]["|".join(p[0:curOrder])] = 1
        else:
            mots[lastNode] = {"|".join(p[0:curOrder]): 1}

    # Update lastNode to what the user just said
    lastNode = "|".join(p[-curOrder:])
    
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
        curOrder = min(cfg["order"],len(p)-1)
        
        for i in range(len(p)-curOrder):
            node = "|".join(p[i:i+curOrder])
            if mots.__contains__(node):
                if mots[node].__contains__(p[i+curOrder]):
                    mots[node][p[i+curOrder]] += 1
                else:
                    mots[node][p[i+curOrder]] = 1
            else:
                mots[node] = {p[i+curOrder]: 1}
   
        if len(lastNode)>0:
            if mots.__contains__(lastNode):
                if mots[lastNode].__contains__("|".join(p[0:curOrder])):
                    mots[lastNode]["|".join(p[0:curOrder])] += 1
                else:
                    mots[lastNode]["|".join(p[0:curOrder])] = 1
            else:
                mots[lastNode] = {"|".join(p[0:curOrder]): 1}

        lastNode = "|".join(p[-curOrder:])
        
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
        k = key.replace('\\', '\\\\').replace('"', '\\"')
        left = ""
        color = "#000000"

        if k[0:4]=="END|":    # nœud de début
            left = k.replace("|", " ")
            graphFile.write('\t"%s" [color="#7faf7f" style=filled];\n' % left)
        elif k[-4:]=="|END":  # nœud de fin
            color="#afafaf"
            left = k.replace("|", " ")
            graphFile.write('\t"%s" [color="#af7f7f" style=filled];\n' % left)
        else:                   # nœud de milieu
            left = k.replace("|", " ")
            graphFile.write('\t"%s" [color="#afaf7f" style=filled];\n' % left)

        for item in mots[key]:
            right = ""
            label = mots[key][item]

            i = item.replace('\\', '\\\\').replace('"', '\\"')

            if k[0:4]=="END|":    # nœud de début
                right = " ".join(k.split("|")[1:]) + " " + i
                if right[-4:]==" END":
                    graphFile.write('\t"%s" [color="#af7f7f" style=filled];\n' % right)
            elif k[-4:]=="|END":  # nœud de fin
                right = i.replace("|", " ")
            else:                   # nœud de milieu
                right = " ".join(k.split("|")[1:]) + " " + i
                if right[-4:]==" END":
                    graphFile.write('\t"%s" [color="#af7f7f" style=filled];\n' % right)

            graphFile.write('\t"%s" -> "%s" [color="%s",label="%d"];\n' % (left, right, color, label))

    graphFile.write("}\n")
    graphFile.close()
