#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Version checker"""

bot = None

import subprocess

def init(botInstance):
    """Inits the msgTrigger module"""
    global bot

    bot = botInstance

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdVer, "version")

def cmdVer(data, opts=[]):
    """Gets bot's version"""
    v = subprocess.getoutput("git describe --tags").split("-")

    if len(v) >= 3:
        bot.irc.msg(bot._("Master version: {v}, Current release: {r}, Commit ID: {c}").format(v=v[0], r=v[1], c=v[2]), data["tgt"])
    elif len(v) == 1:
        bot.irc.msg(bot._("Master version: {v}, first release").format(v=v[0]), data["tgt"])
    else:
        bot.irc.msg(bot._("Sorry, git returned garbage. Please import the tags :("), data["tgt"])
