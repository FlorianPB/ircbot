#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markov Chain statistic-based talk :D"""

import data.Markov
import random

bot = None
talk = 0

def init(botInstance):
    """Inits the msgTrigger module"""
    global bot

    data.Markov.initDb()
    data.Markov.bot = botInstance

    bot = botInstance

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdGraph, "graph")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdRandWalk, "randwalk")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdFlood, "flood")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdTalk, "talk")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdShut, "shut")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdRandom, "random")
    bot.irc.hooks["PRIVMSG"].append(talkCheck)

def cmdRandWalk(data, opts=[]):
    """Sets if random walk or not.
    randwalk {on,off}"""

    if len(opts) >= 1 and ["on", "off"].__contains__(opts[0].lower()):
        if opts[0].lower() == "on":
            data.Markov.cfg["randomWalk"] = True
        else:
            data.Markov.cfg["randomWalk"] = False

def cmdGraph(data, opts=[]):
    """Print graph info
    graph [branch]: print children
    graph: infos on graph
    graph dump <path>: dump graph to <file> (.dot format)"""

    if len(opts)<1:
        bot.irc.msg("Word graph contains %d nodes" % len(data.Markov.mots), data["tgt"])
        bot.irc.msg("Word graph has a depth of %d" % data.Markov.cfg["order"], data["tgt"])
        if data.Markov.cfg["randomWalk"]:
            bot.irc.msg("Word graph is walked randomly", data["tgt"])
        else:
            bot.irc.msg("Word graph is walked randomly, respective to each sequence frequency", data["tgt"])        
        return

    if len(opts)>=2 and opts[0] == "dump":
        data.Markov.dumpGraph(" ".join(opts[1:]))
        return

    for item in opts:
        if data.Markov.mots.__contains__(item):
            bot.irc.msg("%s: %s" % (item, data.Markov.mots[item]), data["tgt"])
        else:
            bot.irc.msg("%s: nothing found" % item, data["tgt"])

def cmdFlood(data, opts=[]):
    """Completely free the bot to talk whenever someone says something"""
    global talk
    talk = 2

def cmdTalk(data, opts=[]):
    """Lets the bot talk"""
    global talk
    talk = 1

def cmdShut(data, opts=[]):
    """Makes the bot be quiet"""
    global talk
    talk = 0

def cmdRandom(data, opts=[]):
    """Says a random sentence"""
    if data["tgt"][0] != "#":
        return

    bot.irc.msg(data.Markov.computeRandomSentence(False), data["tgt"])

def talkCheck(evt):
    """Hook for the event PRIVMSG"""

    user = evt[0][1:].split("!")[0]
    tgt = evt[2]
    txt = (" ".join(evt[3:])[1:]).lower()

    if tgt==bot.cfg["nick"]:
        tgt = user
    
    if talk>0:
        # Last conditions tells the bot to just shut up if he doesn't know what to say next (unless we're in mode 2, then he _must_ talks)
        msg = data.Markov.compute(txt)
        if msg!="":
            bot.irc.msg(msg, tgt)
    else:
        data.Markov.AnalyzeSentence(txt)
