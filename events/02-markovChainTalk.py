#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markov Chain statistic-based talk :D"""

import extern.MarkovTalk

bot = None
talk = False

def init(botInstance):
    """Inits the msgTrigger module"""
    global bot

    extern.MarkovTalk.initDb()
    extern.MarkovTalk.bot = botInstance

    bot = botInstance

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdTalk, "talk", [":.*!~adriens33@"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdShut, "shut", [":.*!~adriens33@"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdRandom, "random")
    bot.irc.hooks["PRIVMSG"].append(talkCheck)

def cmdTalk(data, opts=[]):
    """Let's the bot talk"""
    global talk
    talk = True

def cmdShut(data, opts=[]):
    """Makes the bot be quiet"""
    global talk
    talk = False

def cmdRandom(data, opts=[]):
    """Says a random sentence"""
    if data["tgt"][0] != "#":
        return

    bot.irc.msg(extern.MarkovTalk.computeRandomSentence(), data["tgt"])

def talkCheck(evt):
    """Hook for the event PRIVMSG"""

    user = evt[0][1:].split("!")[0]
    tgt = evt[2]
    txt = " ".join(evt[3:])[1:]

    if tgt==bot.cfg["nick"]:
        tgt = user
    
    if talk:
        bot.irc.msg(extern.MarkovTalk.compute(txt.lower()), tgt)
    else:
        extern.MarkovTalk.AnalyzeSentence(txt.lower())
