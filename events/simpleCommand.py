#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""Get commands from irc"""

import re

import util.cfg
import util.exceptions

moduleData = {
        "cmdChar": "@",
        "access": {
            "stop": [":adriens33!~adriens33@(home|homer)\.art-software\.fr"]
        }
}
registeredCmd = {}
initData = {}

##### INIT the module (needed) #####
def init(data):
    data["irc"].hooks["PRIVMSG"].append(recvCommand)
    util.cfg.default = moduleData
    moduleData = util.cfg.load("commands.json")
    initData = data

##### register main cmds #####
def regMainCmds():
    """Register main commands provided here"""
    registeredCmd["stop"] = cmdStop

##### hook functions #####
def recvCommand(evt):
    """Receive commands from IRC and dispatch them"""
    if len(evt)<4 or evt[1]!="PRIVMSG":
        return
    
    user = evt[0][1:].split("!")[0]
    tgt = evt[2]
    cmd = [evt[3][1:]]
    canRun = True
    # We got some parameters here.. :]
    if len(evt)>4:
        cmd += evt[4:]

    # If user talked to us in private message, answers him the same way
    if tgt==irc.nick:
        tgt=user

    # No command char ? meh. Certainly a dumb user who is just talking.
    # Nevermind. *going back to sleep*
    if cmd[0]!=moduleData["cmdChar"]:
        return

    # Check execution privileges
    if moduleData["access"].__contains__(cmd[0][1:]):
        matches = 0
        for pattern in moduleData["access"][cmd[0][1:]]:
            if re.search(pattern, evt[0]) != None:
                matches+=1
        if matches == 0:
            canRun == False

    # Run command, if it was registered
    if registeredCmd.__contains__(cmd[0][1:]):
        if len(cmd)>1:
            registeredCmd[cmd[0][1:]](irc, cmd[1:])
        else:
            registeredCmd[cmd[0][1:]](irc)

###### Main commands #####
def cmdStop(reason="bye guys !"):
    """Stop the bot properly"""
    raise util.exceptions.StopException
