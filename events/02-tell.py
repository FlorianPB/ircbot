#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tell someone something when they come back"""

from time import strftime

bot = None

txtStack = {}

def init(botInstance):
    """Inits the module"""
    global bot

    bot = botInstance

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdTell, "tell")
    bot.irc.hooks["PRIVMSG"].append(tellCheck)
    bot.irc.hooks["JOIN"].append(tellCheck)

def cmdTell(data, opts=[]):
    """Stack a text for someone to tell
    tell nick text to say"""
    global txtStack

    if len(opts)<2:
        bot.irc.msg(bot._("Please tell me who you want to talk to, and the message!"), data["tgt"])
        return

    nick = opts[0]
    txt = " ".join(opts[1:])

    if not txtStack.__contains__(data["tgt"]):
        txtStack[data["tgt"]] = {nick: [(data["user"], txt, strftime("%F %R")), ]}
    elif not txtStack[data["tgt"]].__contains__(nick):
        txtStack[data["tgt"]][nick] = [(data["user"], txt, strftime("%F %R")),]
    else:
        txtStack[data["tgt"]][nick].append((data["user"], txt, strftime("%F %R")))

    bot.irc.msg(data["user"]+bot._(": Done."), data["tgt"])

def tellCheck(evt):
    """Check if need to say something"""
    global txtStack
    chan = evt[2]
    nick = evt[0].split("!")[0][1:]

    if not txtStack.__contains__(chan):
        return
    if not txtStack[chan].__contains__(nick):
        return
    if len(txtStack[chan][nick])<1:
        return

    item = txtStack[chan][nick].pop()
    sender, msg, ts = item
    
    bot.irc.msg(nick+": <"+sender+"> " + msg + " (" + ts + ")", chan)

    while len(txtStack[chan][nick]) > 0:
        item = txtStack[chan][nick].pop()
        sender, msg, ts = item
        bot.irc.msg(nick+": <"+sender+"> " + msg + " (" + ts + ")", chan)
