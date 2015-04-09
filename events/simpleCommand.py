#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""Get commands from irc

init(data): init the module
registerCommand(command, name, accessRules): register command under name, with optionnal accessRules list
recvCommand(evt): run command detection against the current event line (space-splitted)"""

import re

import util.cfg
import util.exceptions
import util.log

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
    global moduleData, initData

    data["irc"].hooks["PRIVMSG"].append(recvCommand)
    util.cfg.default = moduleData
    moduleData = util.cfg.load("commands.json")
    initData = data

    # Register standard commands
    regMainCmds()

##### register main cmds #####
def regMainCmds():
    """Register main commands provided here"""
    global registeredCmd

    registeredCmd["stop"] = cmdStop
    registeredCmd["modules"] = cmdListModules

def registerCommand(command, name, accessRules=[]):
    """Register a command."""
    global registeredCmd, moduleData
    registeredCmd[name] = command

    initData["log"]("Registered command %s" % name, "events.simpleCommands.registerCommand", util.log.INFO)

    # Have some access rules ? register them and write them for future use (if we don't already have them).
    if len(accessRules)>0 and not moduleData["access"].__contains__(name):
        moduleData["access"][name] = accessRules
        util.cfg.save(moduleData, "commands.json")


##### hook functions #####
def recvCommand(evt):
    """Receive commands from IRC and dispatch them"""
    if len(evt)<4 or evt[1]!="PRIVMSG":
        return
    
    user = evt[0][1:].split("!")[0]
    tgt = evt[2]
    cmd = [evt[3][1:]]
    # We got some parameters here.. :]
    if len(evt)>4:
        cmd += evt[4:]

    # If user talked to us in private message, answers him the same way
    if tgt==initData["irc"].nick:
        tgt=user

    # No command char ? meh. Certainly a dumb user who is just talking.
    # Nevermind. *going back to sleep*
    if cmd[0][0]!=moduleData["cmdChar"]:
        return

    # Check execution privileges
    if moduleData["access"].__contains__(cmd[0][1:]):
        matches = 0
        for pattern in moduleData["access"][cmd[0][1:]]:
            if re.search(pattern, evt[0]) != None:
                matches+=1
        if matches == 0 and len(moduleData["access"][cmd[0][1:]])>0:
            initData["log"]("%s have no right to run %s" % (user, cmd[0][1:]), "events.simpleCommand.recvCommand", util.log.DEBUG)
            initData["connect"].sendText("PRIVMSG %s :Désolé %s, mais tu n'as pas le droit de faire cela.\r\n" % (tgt, user))
            return

    # Run command, if it was registered
    if registeredCmd.__contains__(cmd[0][1:]):
        initData["log"]("%s is a registered command ! Running it." % cmd[0][1:], "events.simpleCommand.recvCommand", util.log.DEBUG)
        if len(cmd)>1:
            registeredCmd[cmd[0][1:]]({"source":evt[0], "user":user, "tgt": tgt}, cmd[1:])
        else:
            registeredCmd[cmd[0][1:]]({"source":evt[0], "user":user, "tgt": tgt})
    else:
        initData["log"]("%s is not a registered command ! Sorry, I can't do anything. %s" % (cmd[0][1:],",".join(list(registeredCmd.keys()))), "events.simpleCommand.recvCommand", util.log.NOTIF)
        initData["connect"].sendText("PRIVMSG %s :Désolé %s, mais je ne trouve pas la commande %s dans mes modules\r\n" % (tgt, user, cmd[0]))

###### Main commands #####
def cmdStop(data, reason="bye guys !"):
    """Stop the bot properly"""
    initData["log"]("Stopping the bot", "events.simpleCommand.cmdStop", util.log.DEBUG)
    raise util.exceptions.StopException("stop command triggered")

def cmdListModules(data):
    """List loaded modules"""
    initData["connect"].sendText("PRIVMSG %s :Loaded modules: %s\r\n" % (data["tgt"], ",".join(list(initData["modules"].keys()))))
