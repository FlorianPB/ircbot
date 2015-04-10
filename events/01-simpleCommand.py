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

    registerCommand(cmdStop, "stop", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    registerCommand(cmdAccess, "access", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    registerCommand(cmdListModules, "modules")
    registerCommand(cmdHelp, "help")
    registerCommand(cmdSay, "say")
    registerCommand(cmdDo, "do")

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

    # Strip from empty items on the start (mainly because of spaces)
    while len(cmd)>1 and len(cmd[0])<1:
        del cmd[0]

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
            initData["irc"].msg("Désolé %s, mais tu n'as pas le droit de faire cela." % user, tgt)
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
        initData["irc"].msg("Désolé %s, mais je ne trouve pas la commande %s dans mes modules." % (user, cmd[0]), tgt)

###### Main commands #####
def cmdStop(data, opts=[]):
    """Stop the bot properly"""

    initData["log"]("Stopping the bot", "events.simpleCommand.cmdStop", util.log.DEBUG)
    raise util.exceptions.StopException("stop command triggered")

def cmdListModules(data, opts=[]):
    """List loaded modules"""

    initData["irc"].msg("Loaded modules: %s" % ",".join(list(initData["modules"].modules.keys())), data["tgt"])

def cmdHelp(data, opts=[]):
    """Display some help.
    help command1 [command2 [command3 […]]]: display command's helptext
    help module module1 [module2 [module3 […]]]: display module's helptext"""
    from time import sleep

    # Show docstring as help
    if len(opts)==0:
        initData["irc"].msg("Available commands: %s" % ",".join(list(registeredCmd.keys())), data["tgt"])
    else:

        # First param = module ? show module docstring
        if opts[0] == "module":
            del opts[0]

            # Show help for each element
            while len(opts)>=1:
                if initData["modules"].modules.keys().__contains__(opts[0]):
                    initData["irc"].msg("Help for module "  + opts[0] + ":", data["tgt"])
                    for line in initData["modules"].modules[opts[0]].__doc__.split("\n"):
                        initData["irc"].msg(line, data["tgt"])
                else:
                    initData["irc"].msg("Cannot find help for module '%s'" % opts[0], data["tgt"])
                del opts[0]
                if len(opts)>0:
                    sleep(1)
        else:

            # Show help for each element
            while len(opts)>=1:
                if registeredCmd.__contains__(opts[0]):
                    initData["irc"].msg("Help for command "  + opts[0] + ":", data["tgt"])
                    for line in registeredCmd[opts[0]].__doc__.split("\n"):
                        initData["irc"].msg(line, data["tgt"])
                else:
                    initData["irc"].msg("Cannot find help for command '%s'" % opts[0], data["tgt"])
                del opts[0]
                if len(opts)>0:
                    sleep(1)

def cmdSay(data, opts=[]):
    """Say something onto a defined channel (or the current one if not specified).
    say [channel] blah blah"""

    tgt = data["tgt"]
    if len(opts)>=2 and initData["irc"].chans.__contains__(opts[0]):
        tgt = opts[0]
        del opts[0]

    initData["irc"].msg(" ".join(opts[0:]), tgt)

def cmdDo(data, opts=[]):
    """Do an action.
    do [channel] blah blah"""
    
    tgt = data["tgt"]
    if len(opts)>=2 and initData["irc"].chans.__contains__(opts[0]):
        tgt = opts[0]
        del opts[0]

    initData["irc"].msg("\x01ACTION " + " ".join(opts[0:]) + "\x01", tgt)

def cmdAccess(data, opts=[]):
    """Manages access to commands
    access command: list user able to run the command (if the command is restricted)
    access command del number: del the numberth access list element for command
    access command add rule [rule2 […]]: add access rule to command
    access command edit ruleNumber ruleContent"""
    global moduleData

    if len(opts) == 1:
        # Check rules for a defined command
        if not moduleData["access"].__contains__(opts[0]):
            initData["irc"].msg("This command is not restricted or does not exist.", data["tgt"])
        else:
            initData["irc"].msg("Access is granted to this command to :", data["tgt"])

            # Command found, list the rules
            num = 0
            for rule in moduleData["access"][opts[0]]:
                initData["irc"].msg("%d: '%s'" % (num, rule), data["tgt"])
                num += 1

    elif len(opts)>=3:
        # Delete a rule
        if opts[1] == "del":
            if len(moduleData["access"][opts[0]]) > opts[2]:
                del moduleData["access"][opts[0]][opts[2]]
                initData["irc"].msg("Rule deleted.", data["tgt"])

            if len(moduleData["access"][opts[0]]) == 0:
                initData["irc"].msg("No rule left, command is now unrestricted." % data["user"], data["tgt"])
                del moduleData["access"][opts[0]]

        # Add rules
        if opts[1] == "add":
            if not moduleData["access"].__contains__(opts[0]):
                initData["irc"].msg("Command was not restricted, registering it into the access list", data["tgt"])
                moduleData["access"][opts[0]] = []

            for rule in opts[2:]:
                moduleData["access"][opts[0]].append(rule)
            initData["irc"].msg("Rule(s) added.", data["tgt"])

        # Edit a rule
        if opts[1] == "edit" and len(opts) == 4:
            if not moduleData["access"].__contains__(opts[0]):
                initData["irc"].msg("This command is not restricted or does not exist.", data["tgt"])
            else:
                if int(opts[2]) >= len(moduleData["access"][opts[0]]):
                    initData["irc"].msg("This rule number is invalid for this command.", data["tgt"])
                else:
                    moduleData["access"][opts[0]][int(opts[2])] = opts[3]

        # Write everything back to the file
        util.cfg.save(moduleData, "commands.json")
