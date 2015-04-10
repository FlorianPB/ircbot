#!/usr/bin/env python3
# -*- coding: utf8 -*-

import re
from random import randint

import util.cfg

initData = {}
triggers = {}

def init(data):
    """Inits the msgTrigger module"""
    global initData, triggers

    initData = data

    util.cfg.default = triggers
    triggers = util.cfg.load("triggers.json")

    data["modules"].modules["01-simpleCommand"].registerCommand(cmdDef, "def", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])

def cmdDef(data, opts=[]):
    """Defines a new trigger and it's associated message (or add a message to an existing trigger if it already exists)
    def triggerName expr expression
    def triggerName msg message
    variables: %user=user name"""
    global triggers

    if len(opts)<3:
        initData["irc"].msg("Sorry! Not enought parameters. See help.", data["tgt"])
        return

    if opts[1] == "expr":
        # Sets the regular expression
        if not triggers.__contains__(opts[0]):
            triggers[opts[0]] = {"expr": " ".join(opts[2:]), "msg":[]}
        else:
            triggers[opts[0]]["expr"] = " ".join(opts[2:])
        initData["irc"].msg("%s> Expression set for Trigger '%s'" % (data["user"], opts[0]), data["tgt"])

    elif opts[1] == "msg":
        # Adds a message
        if not triggers.__contains__(opts[0]):
            triggers[opts[0]] = {"expr": " ", "msg":[]}
        triggers[opts[0]]["msg"].append(" ".join(opts[2:]))
        initData["irc"].msg("%s> Message added for Trigger '%s'" % (data["user"], opts[0]), data["tgt"])
    else:
        initData["irc"].msg("Sorry! Subcommand %s unknown." % opts[1], data["tgt"])

    util.cfg.save(triggers, "triggers.json")

def msgHook(evt):
    """Hook for the event PRIVMSG"""
    user = evt[0][1:].split("!")[0]
    tgt = evt[2]
    txt = " ".join(evt[3:])[1:]

    if tgt==initData["irc"].nick:
        tgt = user

    for triggerName in triggers:
        if re.search(triggerName["expr"], txt) != None:
            answer = triggerName["msg"][randint(0, len(triggerName["msg"]))]
            initData["irc"].msg(answer.replace("%user", user), tgt)
