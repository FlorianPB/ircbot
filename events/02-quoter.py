#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quoter module"""

bot = None
quoteBD = {}
lastUserPhrase = {}

import util.cfg
from random import randint

def init(botInstance):
    """Inits the module"""
    global bot, quoteBD

    bot = botInstance
    util.cfg.default = quoteBD
    quoteBD = util.cfg.load("cfg/quote.json")

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdQuote, "quote")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdSaid, "said")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdQuotes, "quotes")
    bot.irc.hooks["PRIVMSG"].append(getPotentialQuotes)

def cmdQuotes(data, opts=[]):
    """quotes <nick>
    Tells a random <nick>'s quote."""
    global quoteBD

    quoteBD = util.cfg.load("cfg/quote.json")
    if len(quoteBD.keys())>0:
        if len(opts)>0:
            name = opts[0]
        else:
            names = quoteBD.keys()
            name = names[randint(0, len(names)-1)]

        if quoteBD.__contains__(name):
            quotes = quoteBD[name]
            bot.irc.msg("« " + quotes[randint(0, len(quotes)-1)] + " » — " + name, data["tgt"])

def cmdQuote(data, opts=[]):
    """quote <nick>
    Saves the last thing <nick> said."""
    global quoteBD, lastUserPhrase

    if len(opts)>0:
        if lastUserPhrase.__contains__(opts[0]):
            if quoteBD.__contains__(opts[0]):
                quoteBD[opts[0]].append(lastUserPhrase[opts[0]])
            else:
                quoteBD[opts[0]] = [lastUserPhrase[opts[0]], ]
        else:
            bot.irc.msg(opts[0] + "didn't say anything yet !", data["tgt"])
    util.cfg.save(quoteBD, "cfg/quote.json")

def cmdSaid(data, opts=[]):
    """said <nick>
    Shows what <nick> said last."""
    global lastUserPhrase

    if len(opts)>0:
        if lastUserPhrase.__contains__(opts[0]):
            bot.irc.msg("« " + lastUserPhrase[opts[0]] + " » — " + opts[0], data["tgt"])
        else:
            bot.irc.msg(opts[0] + "didn't say anything yet !", data["tgt"])

def getPotentialQuotes(evt):
    """Quotes every last phrase of all users"""
    global lastUserPhrase

    user = evt[0][1:].split("!")[0]
    txt = (" ".join(evt[3:])[1:])

    lastUserPhrase[user] = txt
