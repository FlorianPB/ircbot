#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
            "stop": [":.*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"],
            "kill": [":.*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"],
            "start": [],    # from console only
            "restart": [":.*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"]
        }
}
registeredCmd = {}
bot = None

##### INIT the module (needed) #####
def init(botInstance):
    global moduleData, bot

    bot = botInstance

    bot.irc.hooks["PRIVMSG"].append(recvCommand)
    util.cfg.default = moduleData
    moduleData = util.cfg.load("cfg/commands.json")

##### register commands #####
def registerCommand(command, name, accessRules=[]):
    """Register a command."""
    global registeredCmd, moduleData
    registeredCmd[name] = command

    bot.log.log(bot._("Registered command %s") % name, "events.simpleCommands.registerCommand", util.log.INFO)

    # Have some access rules ? register them and write them for future use (if we don't already have them).
    if len(accessRules)>0 and not moduleData["access"].__contains__(name):
        moduleData["access"][name] = accessRules
        util.cfg.save(moduleData, "cfg/commands.json")


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
    if tgt==bot.cfg["nick"]:
        tgt=user

    # Strip from empty items on the start (mainly because of spaces)
    while len(cmd)>1 and len(cmd[0])<1:
        del cmd[0]

    # No command char ? meh. Certainly a dumb user who is just talking.
    # Nevermind. *going back to sleep*
    if len(cmd) == 0 or len(cmd[0]) == 0 or cmd[0][0]!=moduleData["cmdChar"]:
        return

    # Check execution privileges
    if moduleData["access"].__contains__(cmd[0][1:]):
        matches = 0

        # Local admin console: You can do everything you want, no execution checking! You are the fucking root user! :]
        if evt[0] == ":admin!~admin@localhost" and evt[2] == "/dev/console":
            matches = 1
        else:
            # 'Normal' channel message, so verify carefully who is asking what.
            for pattern in moduleData["access"][cmd[0][1:]]:
                if re.search(pattern, evt[0]) != None:
                    matches+=1
            if matches == 0 and len(moduleData["access"][cmd[0][1:]])>0:
                bot.log.log(bot._("%s have no right to run %s") % (user, cmd[0][1:]), "events.simpleCommand.recvCommand", util.log.DEBUG)
                bot.irc.msg(bot._("Sorry %s, you aren't authorized to do this.") % user, tgt)
                return

    # Run command, if it was registered
    if registeredCmd.__contains__(cmd[0][1:]):
        bot.log.log(bot._("%s is a registered command ! Running it.") % cmd[0][1:], "events.simpleCommand.recvCommand", util.log.DEBUG)
        if len(cmd)>1:
            registeredCmd[cmd[0][1:]]({"source":evt[0], "user":user, "tgt": tgt}, cmd[1:])
        else:
            registeredCmd[cmd[0][1:]]({"source":evt[0], "user":user, "tgt": tgt})
    else:
        bot.log.log(bot._("%s is not a registered command ! Sorry, I can't do anything. %s") % (cmd[0][1:],",".join(list(registeredCmd.keys()))), "events.simpleCommand.recvCommand", util.log.NOTIF)
        bot.irc.msg(bot._("Sorry %s, I can't find %s in my modules.") % (user, cmd[0]), tgt)
