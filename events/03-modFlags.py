#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""Manages the user flags (voice, op)"""

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
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdKick, "kick", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdTopic, "topic", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])

    util.cfg.default = userFlags
    userFlags = util.cfg.load("flags.json")

##### Hook #####
def joinHook(evt):
    """Sets flags on join"""
    nick = evt[0][1:].split("!")[0]

    if userFlags.__contains__(evt[2]):
        for ident in userFlags[evt[2]].keys():
            if re.search(ident, nick) != None and userFlags[evt[2]][ident] != "":
                bot.connect.sendText("MODE " + evt[2] + " " + userFlags[evt[2]][ident] + " " + nick + "\r\n")

##### Commands #####
def cmdVoice(data, opts=[]):
    """Voice someone.
    voice nick [channel if private message] [regex]: voices someone, with a optionnal regex to apply to the nick the next time he joins."""
    global userFlags

    nick = opts[0]
    toSave = nick
    chan = data["tgt"]


    if chan[0]!="#" and len(opts)>=2:
        chan = opts[1]
        del opts[1]

    if chan[0]!="#":
        bot.irc.msg("Channel not specified!", data["tgt"])
        return

    if not userFlags.__contains__(chan):
        userFlags[chan] = {}

    if len(opts)==2:
        toSave = opts[1]

    if not userFlags[chan].__contains__(toSave):
        userFlags[chan][toSave] = "+v"
    elif userFlags[chan][toSave].find("+v") == -1:
        userFlags[chan][toSave] += "+v"

    bot.connect.sendText("MODE " + chan + " +v " + nick + "\r\n")
    util.cfg.save(userFlags, "flags.json")


def cmdDevoice(data, opts=[]):
    """Devoice someone.
    devoice nick [channel if private message] [regex]: devoices someone, with a optionnal regex to apply to the nick the next time he joins."""
    global userFlags

    nick = opts[0]
    toSave = nick
    chan = data["tgt"]

    if chan[0]!="#" and len(opts)>=2:
        chan = opts[1]
        del opts[1]

    if chan[0]!="#":
        bot.irc.msg("Channel not specified!", data["tgt"])
        return

    if not userFlags.__contains__(chan):
        userFlags[chan] = {}

    if len(opts)==2:
        toSave = opts[1]

    if not userFlags[chan].__contains__(toSave):
        userFlags[chan][toSave] = "-v"
    elif userFlags[chan][toSave].find("+v") != -1:
        userFlags[chan][toSave] = userFlags[chan][toSave].replace("+v", "")
        if userFlags[chan][toSave] == "":
            del userFlags[chan][toSave]

    bot.connect.sendText("MODE " + chan + " -v " + nick + "\r\n")
    util.cfg.save(userFlags, "flags.json")

def cmdOp(data, opts=[]):
    """Op someone.
    op nick [channel if private message] [regex]: op someone, with a optionnal regex to apply to the nick the next time he joins."""
    global userFlags

    nick = opts[0]
    toSave = nick
    chan = data["tgt"]

    if chan[0]!="#" and len(opts)>=2:
        chan = opts[1]
        del opts[1]

    if chan[0]!="#":
        bot.irc.msg("Channel not specified!", data["tgt"])
        return

    if not userFlags.__contains__(chan):
        userFlags[chan] = {}

    if len(opts)==2:
        toSave = opts[1]

    if not userFlags[chan].__contains__(toSave):
        userFlags[chan][toSave] = "+o"
    elif userFlags[chan][toSave].find("+o") == -1:
        userFlags[chan][toSave] += "+o"

    bot.connect.sendText("MODE " + chan + " +o " + nick + "\r\n")
    util.cfg.save(userFlags, "flags.json")

def cmdDeop(data, opts=[]):
    """Deop someone.
    deop nick [channel if private message] [regex]: deop someone, with a optionnal regex to apply to the nick the next time he joins."""
    global userFlags

    nick = opts[0]
    toSave = nick
    chan = data["tgt"]

    if chan[0]!="#" and len(opts)>=2:
        chan = opts[1]
        del opts[1]

    if chan[0]!="#":
        bot.irc.msg("Channel not specified!", data["tgt"])
        return

    if not userFlags.__contains__(chan):
        userFlags[chan] = {}

    if len(opts)==2:
        toSave = opts[1]

    if not userFlags[chan].__contains__(toSave):
        userFlags[chan][toSave] = "-o"
    elif userFlags[chan][toSave].find("+o") != -1:
        userFlags[chan][toSave] = userFlags[chan][toSave].replace("+o", "")
        if userFlags[chan][toSave] == "":
            del userFlags[chan][toSave]

    bot.connect.sendText("MODE " + chan + " -o " + nick + "\r\n")
    util.cfg.save(userFlags, "flags.json")

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
        bot.irc.msg("Channel not specified!", data["tgt"])
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
        bot.irc.msg("Sorry, you need to specify a channel in private mode", data["tgt"])
        return

    bot.connect.sendText("TOPIC " + chan + " :" + " ".join(opts) + "\r\n")
