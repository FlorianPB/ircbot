#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""Log IRC events to channel-separated log files"""

initData = {}

##### INIT the module (needed) #####
def init(data):
    global initData

    initData = data
    data["irc"].hooks["PRIVMSG"].append(logPrivMsgToChat)
    data["irc"].hooks["JOIN"].append(logJoinToChat)
    data["irc"].hooks["PART"].append(logPartFromChat)
    data["irc"].hooks["NICK"].append(logChangeNick)
    data["irc"].hooks["QUIT"].append(logQuitChat)
    data["irc"].hooks["MODE"].append(logSetModeChat)

##### hook functions #####
def logPrivMsgToChat(evt):
    """Print log to text"""
    from time import strftime

    logFile = open("%s.log" % evt[2], "a")
    
    if evt[3] == ":\x01ACTION":
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " * " + evt[0][1:].split("!")[0] + " " + " ".join(evt[4:]) + "\n")
    else:
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " <" + evt[0][1:].split("!")[0] + "> " + " ".join(evt[3:])[1:] + "\n")
    logFile.close()

def logJoinToChat(evt):
    """Print log to text"""
    from time import strftime

    logFile = open("%s.log" % evt[2], "a")
    
    logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " → " + evt[0][1:].split("!")[0] + " a rejoint le canal\n")
    logFile.close()

def logChangeNick(evt):
    """Print log to text"""
    from time import strftime
    for chan in initData["irc"].chans:
        logFile = open("%s.log" % chan, "a")
    
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " * " + evt[0][1:].split("!")[0] + " est désormais connu sous le nom de " + evt[2][1:] + "\n")

        logFile.close()

def logPartFromChat(evt):
    """Print log to text"""
    from time import strftime

    logFile = open("%s.log" % evt[2], "a")
    
    logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " ← " + evt[0][1:].split("!")[0] + " est parti du canal")
    if len(evt)>=4:
        logFile.write(" (raison: %s)" % " ".join(evt[3:])[1:])
    logFile.write("\n")

    logFile.close()

def logQuitChat(evt):
    """Print log to text"""
    from time import strftime

    for chan in initData["irc"].chans:
        logFile = open("%s.log" % chan, "a")
    
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " ← " + evt[0][1:].split("!")[0] + " s'est déconnecté")
        if len(evt)>=3:
            logFile.write(" (raison: %s)" % " ".join(evt[2:])[1:])
        logFile.write("\n")

        logFile.close()

def logSetModeChat(evt):
    """Print log to text"""
    from time import strftime

    logFile = open("%s.log" % evt[2], "a")
    
    if len(evt) >= 5:
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " * Mode " + evt[3] + " défini pour " + evt[4] + " par " + evt[0][1:].split("!")[0] + "\n")
    else:
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " * Mode " + evt[3] + " défini sur " + evt[2] + " par " + evt[0][1:].split("!")[0] + "\n")
    logFile.close()
