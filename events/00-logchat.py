#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Log IRC events to channel-separated log files"""

bot = None

##### INIT the module (needed) #####
def init(botInstance):
    global bot

    bot = botInstance
    bot.irc.hooks["PRIVMSG"].append(logPrivMsgToChat)
    bot.irc.hooks["JOIN"].append(logJoinToChat)
    bot.irc.hooks["PART"].append(logPartFromChat)
    bot.irc.hooks["NICK"].append(logChangeNick)
    bot.irc.hooks["QUIT"].append(logQuitChat)
    bot.irc.hooks["MODE"].append(logSetModeChat)

##### hook functions #####
def logPrivMsgToChat(evt):
    """Print log to text"""
    from time import strftime

    chan = evt[2]
    if chan == "/dev/console":
        chan = "consoleChan"

    logFile = open("log/%s.log" % chan, "a")
    
    if evt[3] == ":\x01ACTION":
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " * " + evt[0][1:].split("!")[0] + " " + " ".join(evt[4:]).replace("\x01", "") + "\n")
    else:
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " <" + evt[0][1:].split("!")[0] + "> " + " ".join(evt[3:])[1:] + "\n")
    logFile.close()

def logJoinToChat(evt):
    """Print log to text"""
    from time import strftime

    logFile = open("log/%s.log" % evt[2], "a")
    
    logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " → " + evt[0][1:].split("!")[0] + bot._(" joined the channel\n"))
    logFile.close()

def logChangeNick(evt):
    """Print log to text"""
    from time import strftime
    for chan in bot.irc.chans:
        if chan=="/dev/console":
            continue

        logFile = open("log/%s.log" % chan, "a")
    
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " * " + evt[0][1:].split("!")[0] + bot._(" is now known as ") + evt[2][1:] + "\n")

        logFile.close()

def logPartFromChat(evt):
    """Print log to text"""
    from time import strftime

    logFile = open("log/%s.log" % evt[2], "a")
    
    logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " ← " + evt[0][1:].split("!")[0] + bot._(" left the channel"))
    if len(evt)>=4:
        logFile.write(bot._(" (reason: %s)") % " ".join(evt[3:])[1:])
    logFile.write("\n")

    logFile.close()

def logQuitChat(evt):
    """Print log to text"""
    from time import strftime

    for chan in bot.irc.chans:
        if chan == "/dev/console":
            continue

        logFile = open("log/%s.log" % chan, "a")
    
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " ← " + evt[0][1:].split("!")[0] + bot._(" has quit"))
        if len(evt)>=3:
            logFile.write(bot._(" (reason: %s)") % " ".join(evt[2:])[1:])
        logFile.write("\n")

        logFile.close()

def logSetModeChat(evt):
    """Print log to text"""
    from time import strftime

    logFile = open("log/%s.log" % evt[2], "a")
    
    if len(evt) >= 5:
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + bot._(" * Mode %s defined for %s by") % (evt[3], evt[4])  + evt[0][1:].split("!")[0] + "\n")
    else:
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + bot._(" * Mode %s defined on %s by ") % (evt[3], evt[2]) + evt[0][1:].split("!")[0] + "\n")
    logFile.close()
