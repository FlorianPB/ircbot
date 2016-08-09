#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Basic commands
Moved from 01-simpleCommand to avoid having a too big module"""

bot = None

import random
import re

import util.cfg
import util.exceptions
import util.log

def init(botInstance):
    """Inits the module"""
    global bot

    bot = botInstance

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdStop, "stop", [":.*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdKill, "kill", [":.*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdStart, "start", [])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdRestart, "restart", [":.*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdAccess, "access", [":.*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdListModules, "modules")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdHelp, "help")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdSay, "say")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdDo, "do")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdMuffin, "muffin")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdHug, "hug")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdMsg, "msg", [":.*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"])
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdDice, "dice")

### Bot state ###
def cmdStop(data, opts=[]):
    """Stop the bot properly"""
    if not bot.isRunning:
        bot.irc.msg(bot._("Sorry, we already are stopped !"), data["tgt"])
        return

    bot.log.log(bot._("Stopping the bot's irc connection"), "events.simpleCommand.cmdStop", util.log.DEBUG)
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
        bot.irc.msg(bot._("Sorry, we already are started !"), data["tgt"])
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

    bot.irc.msg(bot._("Loaded modules: %s") % ",".join(list(bot.modules.modules.keys())), data["tgt"])

def cmdHelp(data, opts=[]):
    """Display some help.
    help command1 [command2 [command3 […]]]: display command's helptext
    help module module1 [module2 [module3 […]]]: display module's helptext"""
    from time import sleep

    # Show docstring as help
    if len(opts)==0:
        bot.irc.msg(bot._("Available commands: %s") % ",".join(list(bot.modules.modules["01-simpleCommand"].registeredCmd.keys())), data["tgt"])
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
                    bot.irc.msg(bot._("Cannot find help for module '%s'") % opts[0], data["tgt"])
                del opts[0]
                if len(opts)>0:
                    sleep(1)
        else:

            # Show help for each element
            while len(opts)>=1:
                if bot.modules.modules["01-simpleCommand"].registeredCmd.__contains__(opts[0]):
                    bot.irc.msg(bot._("Help for command ")  + opts[0] + ":", data["tgt"])
                    for line in bot.modules.modules["01-simpleCommand"].registeredCmd[opts[0]].__doc__.split("\n"):
                        bot.irc.msg(line, data["tgt"])
                else:
                    bot.irc.msg(bot._("Cannot find help for command '%s'") % opts[0], data["tgt"])
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
            if bot.irc.chans.__contains__(opts[0].lower()):
                chan = opts[0].lower()
                del opts[0]
            elif not bot.irc.chans.__contains__(chan):
                bot.irc.msg(bot._("Sorry, I have no valid channel to work with :/"), data["tgt"])
                return
    else:
        bot.irc.msg(bot._("Sorry, please read @help."), data["tgt"])
        return

    bot.irc.msg(" ".join(opts[0:]), chan)

def cmdDo(data, opts=[]):
    """Do an action.
    do [channel] blah blah"""

    # Checks if there is a valid way to output to some connected channel
    chan = data["tgt"]
    if len(opts)>=1:
        if len(opts)>=2:
            if bot.irc.chans.__contains__(opts[0].lower()):
                chan = opts[0].lower()
                del opts[0]
            elif not bot.irc.chans.__contains__(chan):
                bot.irc.msg(bot._("Sorry, I have no valid channel to work with :/"), data["tgt"])
                return
    else:
        bot.irc.msg(bot._("Sorry, please read @help."), data["tgt"])
        return

    bot.irc.msg("\x01ACTION " + " ".join(opts[0:]) + "\x01", chan)

# Muffin ! Yummy !
def cmdMuffin(data, opts=[]):
    """Sends a muffin on someone.
    muffin nick [channel]"""

    from random import randint
    from time import sleep

    # Checks if there is a valid way to output to some connected channel
    chan = data["tgt"]
    if len(opts)>=1:
        if len(opts)>=2:
            if bot.irc.chans.__contains__(opts[-1].lower()):
                chan = opts[-1].lower()
                opts = opts[:-1]
            elif not bot.irc.chans.__contains__(chan):
                bot.irc.msg(bot._("Sorry, I have no valid channel to work with :/"), data["tgt"])
                return
    else:
        bot.irc.msg(bot._("Sorry, please read @help."), data["tgt"])
        return
    
    for nick in opts:
        speed = randint(30, 2000)
        bot.irc.msg("\x01ACTION " + bot._("launches a muffin on %s at %d km/h") % (nick, speed) + "\x01\r\n", chan)
        if speed>=1224:
            bot.irc.msg(bot._("5MU4FF8IN9 RA11IN12BO2OM6 !!") + "\r\n", chan)
        sleep(0.25)

def cmdDice(data, opts=[]):
    """Rolls dice(s).
    dice [faces (6)] [quantity (1)]"""
    faces = 6
    q = 1
    if len(opts)>0:
        faces = int(opts[0])
        if len(opts)>1:
            q = int(opts[1])

    if q < 1:
        return

    if faces < 2:
        return
    
    if q > 50:
        return
    
    bot.irc.msg(" ".join(["%d" % random.randint(1, faces) for dice in range(q)]), data["tgt"])

# Hugs someone if they need it *sqeaks*
def cmdHug(data, opts=[]):
    """Hugs someone.
    hug nick [channel]"""

    from random import randint
    from time import sleep

    # Checks if there is a valid way to output to some connected channel
    chan = data["tgt"]
    if len(opts)>=1:
        if len(opts)>=2:
            if bot.irc.chans.__contains__(opts[-1].lower()):
                chan = opts[-1].lower()
                opts = opts[:-1]
            elif not bot.irc.chans.__contains__(chan):
                bot.irc.msg(bot._("Sorry, I have no valid channel to work with :/"), data["tgt"])
                return
    else:
        bot.irc.msg(bot._("Sorry, please read @help."), data["tgt"])
        return
    
    for nick in opts:
        bot.irc.msg("\x01ACTION " + bot._("hugs %s very gently") % nick + "\x01\r\n", chan)
        sleep(0.25)


##### Command access rules. Wait man, this is serious shit done down there. Don't touch. #####
def cmdAccess(data, opts=[]):
    """Manages access to commands
    access command: list user able to run the command (if the command is restricted)
    access command del number: del the numberth access list element for command
    access command add rule [rule2 […]]: add access rule to command
    access command edit ruleNumber ruleContent"""

    if len(opts) == 1:
        # Check rules for a defined command
        if not bot.modules.modules["01-simpleCommand"].moduleData["access"].__contains__(opts[0]):
            bot.irc.msg(bot._("This command is not restricted or does not exist."), data["tgt"])
        else:
            bot.irc.msg(bot._("Access is granted to this command to :"), data["tgt"])

            # Command found, list the rules
            num = 0
            for rule in bot.modules.modules["01-simpleCommand"].moduleData["access"][opts[0]]:
                bot.irc.msg("%d: '%s'" % (num, rule), data["tgt"])
                num += 1

    elif len(opts)>=3:
        # Delete a rule
        if opts[1] == "del":
            if int(opts[2]) >= len(bot.modules.modules["01-simpleCommand"].moduleData["access"][opts[0]]):
                    bot.irc.msg(bot._("This rule number is invalid for this command."), data["tgt"])
            else:
                del bot.modules.modules["01-simpleCommand"].moduleData["access"][opts[0]][int(opts[2])]
                bot.irc.msg(bot._("Rule deleted."), data["tgt"])

            if len(bot.modules.modules["01-simpleCommand"].moduleData["access"][opts[0]]) == 0:
                bot.irc.msg(bot._("No rule left, command is now unrestricted."), data["tgt"])
                del bot.modules.modules["01-simpleCommand"].moduleData["access"][opts[0]]

        # Add rules
        if opts[1] == "add":
            if not bot.modules.modules["01-simpleCommand"].moduleData["access"].__contains__(opts[0]):
                bot.irc.msg(bot._("Command was not restricted, registering it into the access list"), data["tgt"])
                bot.modules.modules["01-simpleCommand"].moduleData["access"][opts[0]] = []

            for rule in opts[2:]:
                bot.modules.modules["01-simpleCommand"].moduleData["access"][opts[0]].append(rule)
            bot.irc.msg(bot._("Rule(s) added."), data["tgt"])

        # Edit a rule
        if opts[1] == "edit" and len(opts) == 4:
            if not bot.modules.modules["01-simpleCommand"].moduleData["access"].__contains__(opts[0]):
                bot.irc.msg(bot._("This command is not restricted or does not exist."), data["tgt"])
            else:
                if int(opts[2]) >= len(bot.modules.modules["01-simpleCommand"].moduleData["access"][opts[0]]):
                    bot.irc.msg(bot._("This rule number is invalid for this command."), data["tgt"])
                else:
                    bot.modules.modules["01-simpleCommand"].moduleData["access"][opts[0]][int(opts[2])] = opts[3]
                    bot.irc.msg(bot._("Access rule edited."), data["tgt"])

        # Write everything back to the file
        util.cfg.save(bot.modules.modules["01-simpleCommand"].moduleData, "cfg/commands.json")

# Say something to someone or to a channel (even if not joined)
def cmdMsg(data, opts=[]):
    """Say something to someone or to a channel (even if not joined)
    msg <channel|nickname> blah blah"""

    chan = data["tgt"]

    # Checks if there is a valid way to output to some connected channel
    if len(opts)>=2:
        chan = opts[0].lower()
        del opts[0]
    else:
        bot.irc.msg(bot._("Sorry, I have no valid channel to work with :/"), data["tgt"])
        return

    bot.irc.msg(" ".join(opts[0:]), chan)
