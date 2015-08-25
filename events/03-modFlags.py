#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manages the user flags (voice, op, quiet)"""

import re

import util.cfg

bot = None
userFlags = {}

def init(botInstance):
    global bot, userFlags

    bot = botInstance

    bot.irc.hooks["JOIN"].append(joinHook)
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdVoice, "voice", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdDevoice, "devoice", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdOp, "op", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdDeop, "deop", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdQuiet, "quiet", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdUnquiet, "unquiet", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdKick, "kick", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdTopic, "topic", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])

    util.cfg.default = userFlags
    userFlags = util.cfg.load("cfg/flags.json")

##### Hook #####
def joinHook(evt):
    """Sets flags on join"""
    nick = evt[0][1:].split("!")[0]
    chan = evt[2].lower()

    if userFlags.__contains__(chan):
        for ident in userFlags[chan]:
            if re.search(ident, nick) != None and userFlags[chan][ident] != "":
                bot.connect.sendText("MODE " + chan + " " + userFlags[chan][ident] + " " + nick + "\r\n")

##### Commands #####
def cmdVoice(data, opts=[]):
    """Voice someone.
    voice nick [channel [regex]]: voices someone, with a optionnal regex to apply to the nick the next time he joins."""
    setFlag("v", True, data, opts)

def cmdDevoice(data, opts=[]):
    """Devoice someone.
    devoice nick [channel [regex]]: devoices someone, with a optionnal regex to apply to the nick the next time he joins."""
    setFlag("v", False, data, opts)

def cmdOp(data, opts=[]):
    """Op someone.
    op nick [channel [regex]] op someone, with a optionnal regex to apply to the nick the next time he joins."""
    setFlag("o", True, data, opts)

def cmdDeop(data, opts=[]):
    """Deop someone.
    deop nick [channel [regex]]: deop someone, with a optionnal regex to apply to the nick the next time he joins."""
    setFlag("o", False, data, opts)

def cmdQuiet(data, opts=[]):
    """Quiets someone.
    quiet nick [channel [regex]]: quiets someone, with a optionnal regex to apply to the nick the next time he joins."""
    setFlag("q", True, data, opts)

def cmdUnquiet(data, opts=[]):
    """Unquiets someone.
    unquiet nick [channel [regex]]: unquiets someone, with a optionnal regex to apply to the nick the next time he joins."""
    setFlag("q", False, data, opts)


def setFlag(flag, toState, data, opts=[]):
    """General flag set/unset function"""
    global userFlags

    saveFlag = False
    nick = opts[0]
    toSave = nick
    chan = data["tgt"].lower()

    if chan[0]!="#" and len(opts)>=2:
        chan = opts[1].lower()
        saveFlag = True
        del opts[1]

    if chan[0]!="#":
        bot.irc.msg(bot._("Channel not specified!"), data["tgt"])
        return

    # If you gave channel + regex manually, save the config. Otherwise it's temporary.
    if saveFlag:
        if not userFlags.__contains__(chan):
            userFlags[chan] = {}

        if len(opts)==2:
            toSave = opts[1]

        if not userFlags[chan].__contains__(nick):
            userFlags[chan][toSave] = "-+"[toState] + flag
        elif userFlags[chan][toSave].find("+-"[toState] + flag) == -1:
            userFlags[chan][toSave] += "-+"[toState] + flag

        util.cfg.save(userFlags, "cfg/flags.json")

    bot.connect.sendText("MODE " + chan + " {sign}{flag} ".format(sign="-+"[toState], flag=flag) + nick + "\r\n")

def cmdKick(data, opts=[]):
    """Kicks someone
    kick nick [channel if private] [reason]"""

    nick = opts[0]
    chan = data["tgt"]
    reason = ""

    if chan[0]!="#" and len(opts)>=2:
        chan = opts[1]
        del opts[1]

    if chan[0]!="#":
        bot.irc.msg(bot._("Channel not specified!"), data["tgt"])
        return

    if len(opts)>1:
        reason = " :" + " ".join(opts[1:])

    bot.connect.sendText("KICK " + chan + " " + nick + reason + "\r\n")

def cmdTopic(data, opts=[]):
    """Sets the topic
    topic [chan] Topic bla bla"""

    chan = data["tgt"]
    if chan[0]!='#':
        chan = opts[0]
        del opts[0]

    if chan[0]!='#':
        bot.irc.msg(bot._("Sorry, you need to specify a channel in private mode"), data["tgt"])
        return

    bot.connect.sendText("TOPIC " + chan + " :" + " ".join(opts) + "\r\n")
