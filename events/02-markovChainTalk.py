#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markov Chain statistic-based talk :D"""

import extern.MarkovTalk
import random

bot = None
talk = 0

def init(botInstance):
    """Inits the msgTrigger module"""
    global bot

    extern.MarkovTalk.initDb()
    extern.MarkovTalk.bot = botInstance

    bot = botInstance

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdFlood, "flood")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdTalk, "talk")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdShut, "shut")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdRandom, "random")
    bot.irc.hooks["PRIVMSG"].append(talkCheck)

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

    bot.irc.msg(extern.MarkovTalk.computeRandomSentence(), data["tgt"])

def talkCheck(evt):
    """Hook for the event PRIVMSG"""

    user = evt[0][1:].split("!")[0]
    tgt = evt[2]
    txt = (" ".join(evt[3:])[1:]).lower()

    if tgt==bot.cfg["nick"]:
        tgt = user
    
    if talk>0:
        if txt.find(bot.cfg["nick"].lower())>=0:
            txt = txt.replace(bot.cfg["nick"].lower(), "")
            while ord(txt[0])<ord('a') or ord(txt[0])>ord('z') and txt!='':
                txt = txt[1:]
            bot.irc.msg(extern.MarkovTalk.compute(txt), tgt)
        elif random.random() >= 0.9 or talk>1:
            bot.irc.msg(extern.MarkovTalk.compute(txt), tgt)
        else:
            extern.MarkovTalk.AnalyzeSentence(txt)
    else:
        extern.MarkovTalk.AnalyzeSentence(txt)
