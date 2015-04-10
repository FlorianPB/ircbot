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
    data["modules"].modules["01-simpleCommand"].registerCommand(cmdTrg, "trg")
    data["irc"].hooks["PRIVMSG"].append(msgHook)

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

def cmdTrg(data, opts=[]):
    """List active triggers:
    trg: list all trigger namer
    trg expr name: list expression for trigger name
    trg msg name: list messages for trigger name"""
    from time import sleep

    if len(opts) == 0:
        initData["irc"].msg("Loaded triggers: " + ",".join(list(triggers.keys())), data["tgt"])

    if len(opts) == 2:
        if opts[0] == "expr" and triggers.__contains__(opts[1]):
            initData["irc"].msg("Expression for %s : %s" % (opts[1], triggers[opts[1]]["expr"]), data["tgt"])

        elif opts[0] == "msg" and triggers.__contains__(opts[1]):
            initData["irc"].msg("Message(s) for %s :" % opts[1], data["tgt"])
            nb = 0
            for message in triggers[opts[1]]["msg"]:
                initData["irc"].msg("- %s" % message, data["tgt"])
                nb += 1
                if nb % 8 == 0:
                    sleep(1)

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
