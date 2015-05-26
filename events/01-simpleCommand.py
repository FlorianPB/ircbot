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
            "stop": [":adriens33!~adriens33@(home|homer)\.art-software\.fr"],
            "kill": [":adriens33!~adriens33@(home|homer)\.art-software\.fr"],
            "start": [],    # from console only
            "restart": [":adriens33!~adriens33@(home|homer)\.art-software\.fr"]
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
    moduleData = util.cfg.load("commands.json")

    # Register standard commands
    regMainCmds()

##### register main cmds #####
def regMainCmds():
    """Register main commands provided here"""
    global registeredCmd

    registerCommand(cmdStop, "stop", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    registerCommand(cmdKill, "kill", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    registerCommand(cmdStart, "start", [])
    registerCommand(cmdRestart, "restart", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    registerCommand(cmdAccess, "access", [":adriens33!~adriens33@(home|homer)\.art-software\.fr"])
    registerCommand(cmdListModules, "modules")
    registerCommand(cmdHelp, "help")
    registerCommand(cmdSay, "say")
    registerCommand(cmdDo, "do")
    registerCommand(cmdMuffin, "muffin")

def registerCommand(command, name, accessRules=[]):
    """Register a command."""
    global registeredCmd, moduleData
    registeredCmd[name] = command

    bot.log.log("Registered command %s" % name, "events.simpleCommands.registerCommand", util.log.INFO)

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
    if tgt==bot.cfg["nick"]:
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

        # Local admin console: You can do everything you want, no execution checking! You are the fucking root user! :]
        if evt[0] == ":admin!~admin@localhost" and evt[2] == "/dev/console":
            matches = 1
        else:
            # 'Normal' channel message, so verify carefully who is asking what.
            for pattern in moduleData["access"][cmd[0][1:]]:
                if re.search(pattern, evt[0]) != None:
                    matches+=1
            if matches == 0 and len(moduleData["access"][cmd[0][1:]])>0:
                bot.log.log("%s have no right to run %s" % (user, cmd[0][1:]), "events.simpleCommand.recvCommand", util.log.DEBUG)
                bot.irc.msg("Désolé %s, mais tu n'as pas le droit de faire cela." % user, tgt)
                return

    # Run command, if it was registered
    if registeredCmd.__contains__(cmd[0][1:]):
        bot.log.log("%s is a registered command ! Running it." % cmd[0][1:], "events.simpleCommand.recvCommand", util.log.DEBUG)
        if len(cmd)>1:
            registeredCmd[cmd[0][1:]]({"source":evt[0], "user":user, "tgt": tgt}, cmd[1:])
        else:
            registeredCmd[cmd[0][1:]]({"source":evt[0], "user":user, "tgt": tgt})
    else:
        bot.log.log("%s is not a registered command ! Sorry, I can't do anything. %s" % (cmd[0][1:],",".join(list(registeredCmd.keys()))), "events.simpleCommand.recvCommand", util.log.NOTIF)
        bot.irc.msg("Désolé %s, mais je ne trouve pas la commande %s dans mes modules." % (user, cmd[0]), tgt)

###### Main commands #####

### Bot state ###
def cmdStop(data, opts=[]):
    """Stop the bot properly"""
    if not bot.isRunning:
        bot.irc.msg("Sorry, we already are stopped !", data["tgt"])
        return

    bot.log.log("Stopping the bot's irc connection", "events.simpleCommand.cmdStop", util.log.DEBUG)
    bot.stop()

def cmdKill(data, opts=[]):
    """Really stop the bot (console included)"""
    if bot.isRunning:
        cmdStop(data, opts)

    bot.consoleRunning = False
    raise util.exceptions.StopException()


def cmdStart(data, opts=[]):
    """Starts the bot irc connection from console"""
    if bot.isRunning:
        bot.irc.msg("Sorry, we already are started !", data["tgt"])
        return

    bot.start()

def cmdRestart(data, opts=[]):
    """Stops and restarts the bot's connection and modules"""
    if bot.isRunning:
        bot.stop()

    bot.start()

### Other commands ###
def cmdListModules(data, opts=[]):
    """List loaded modules"""

    bot.irc.msg("Loaded modules: %s" % ",".join(list(initData["modules"].modules.keys())), data["tgt"])

def cmdHelp(data, opts=[]):
    """Display some help.
    help command1 [command2 [command3 […]]]: display command's helptext
    help module module1 [module2 [module3 […]]]: display module's helptext"""
    from time import sleep

    # Show docstring as help
    if len(opts)==0:
        bot.irc.msg("Available commands: %s" % ",".join(list(registeredCmd.keys())), data["tgt"])
    else:

        # First param = module ? show module docstring
        if opts[0] == "module":
            del opts[0]

            # Show help for each element
            while len(opts)>=1:
                if bot.modules.modules.keys().__contains__(opts[0]):
                    bot.irc.msg("Help for module "  + opts[0] + ":", data["tgt"])
                    for line in bot.modules.modules[opts[0]].__doc__.split("\n"):
                        bot.irc.msg(line, data["tgt"])
                else:
                    bot.irc.msg("Cannot find help for module '%s'" % opts[0], data["tgt"])
                del opts[0]
                if len(opts)>0:
                    sleep(1)
        else:

            # Show help for each element
            while len(opts)>=1:
                if registeredCmd.__contains__(opts[0]):
                    bot.irc.msg("Help for command "  + opts[0] + ":", data["tgt"])
                    for line in registeredCmd[opts[0]].__doc__.split("\n"):
                        bot.irc.msg(line, data["tgt"])
                else:
                    bot.irc.msg("Cannot find help for command '%s'" % opts[0], data["tgt"])
                del opts[0]
                if len(opts)>0:
                    sleep(1)

##### Says and dos #####
def cmdSay(data, opts=[]):
    """Say something onto a defined channel (or the current one if not specified).
    say [channel] blah blah"""

    # Checks if there is a valid way to output to some connected channel
    chan = data["tgt"]
    if len(opts)>=1:
        if len(opts)>=2:
            if bot.irc.chans.__contains__(opts[0]):
                chan = opts[0]
                del opts[0]
            elif not bot.irc.chans.__contains__(chan):
                bot.irc.msg("Sorry, I have no valid channel to work with :/", data["tgt"])
                return
    else:
        bot.irc.msg("Sorry, please read @help.", data["tgt"])
        return

    bot.irc.msg(" ".join(opts[0:]), chan)

def cmdDo(data, opts=[]):
    """Do an action.
    do [channel] blah blah"""

    # Checks if there is a valid way to output to some connected channel
    chan = data["tgt"]
    if len(opts)>=1:
        if len(opts)>=2:
            if bot.irc.chans.__contains__(opts[0]):
                chan = opts[0]
                del opts[0]
            elif not bot.irc.chans.__contains__(chan):
                bot.irc.msg("Sorry, I have no valid channel to work with :/", data["tgt"])
                return
    else:
        bot.irc.msg("Sorry, please read @help.", data["tgt"])
        return

    bot.irc.msg("\x01ACTION " + " ".join(opts[0:]) + "\x01", chan)

# Muffin ! Yummy !
def cmdMuffin(data, opts=[]):
    """Sends a muffin on someone.
    muffin nick [channel]"""

    from random import randint

    # Checks if there is a valid way to output to some connected channel
    chan = data["tgt"]
    if len(opts)>=1:
        if len(opts)>=2:
            if bot.irc.chans.__contains__(opts[1]):
                chan = opts[1]
            elif not bot.irc.chans.__contains__(chan):
                bot.irc.msg("Sorry, I have no valid channel to work with :/", data["tgt"])
                return
    else:
        bot.irc.msg("Sorry, please read @help.", data["tgt"])
        return
    
    speed = randint(30, 2000)
    bot.irc.msg("\x01ACTION lance un muffin sur " + opts[0] + " à %d km/h\r\n" % speed, chan)
    if speed>=1224:
        bot.irc.msg("MUFFIN RAINBOOM !!\r\n", chan)

##### Command access rules. Wait man, this is serious shit done down there. Don't touch. #####
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
            bot.irc.msg("This command is not restricted or does not exist.", data["tgt"])
        else:
            bot.irc.msg("Access is granted to this command to :", data["tgt"])

            # Command found, list the rules
            num = 0
            for rule in moduleData["access"][opts[0]]:
                bot.irc.msg("%d: '%s'" % (num, rule), data["tgt"])
                num += 1

    elif len(opts)>=3:
        # Delete a rule
        if opts[1] == "del":
            if int(opts[2]) >= len(moduleData["access"][opts[0]]):
                    bot.irc.msg("This rule number is invalid for this command.", data["tgt"])
            else:
                del moduleData["access"][opts[0]][int(opts[2])]
                bot.irc.msg("Rule deleted.", data["tgt"])

            if len(moduleData["access"][opts[0]]) == 0:
                bot.irc.msg("No rule left, command is now unrestricted.", data["tgt"])
                del moduleData["access"][opts[0]]

        # Add rules
        if opts[1] == "add":
            if not moduleData["access"].__contains__(opts[0]):
                bot.irc.msg("Command was not restricted, registering it into the access list", data["tgt"])
                moduleData["access"][opts[0]] = []

            for rule in opts[2:]:
                moduleData["access"][opts[0]].append(rule)
            bot.irc.msg("Rule(s) added.", data["tgt"])

        # Edit a rule
        if opts[1] == "edit" and len(opts) == 4:
            if not moduleData["access"].__contains__(opts[0]):
                bot.irc.msg("This command is not restricted or does not exist.", data["tgt"])
            else:
                if int(opts[2]) >= len(moduleData["access"][opts[0]]):
                    bot.irc.msg("This rule number is invalid for this command.", data["tgt"])
                else:
                    moduleData["access"][opts[0]][int(opts[2])] = opts[3]
                    bot.irc.msg("Access rule edited.", data["tgt"])

        # Write everything back to the file
        util.cfg.save(moduleData, "commands.json")
