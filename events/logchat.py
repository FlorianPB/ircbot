#!/usr/bin/env python3
# -*- coding: utf8 -*-

def init(irc):
    irc.hooks["PRIVMSG"].append(logPrivMsgToChat)
    irc.hooks["JOIN"].append(logJoinToChat)
    irc.hooks["PART"].append(logPartFromChat)

def logPrivMsgToChat(irc, evt):
    """Print log to text"""
    from time import strftime

    evt = evt.split()
    logFile = open("%s.log" % evt[2], "a")
    
    logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + "<" + evt[0][1:].split("!")[0] + "> " + evt[3:][1:] + "\n")
    logFile.close()

def logJoinToChat(irc, evt):
    """Print log to text"""
    from time import strftime

    evt = evt.split()
    logFile = open("%s.log" % evt[2], "a")
    
    logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + "→ " + evt[0][1:].split("!")[0] + " a rejoint le canal\n")
    logFile.close()

def logPartFromChat(irc, evt):
    """Print log to text"""
    from time import strftime

    evt = evt.split()
    logFile = open("%s.log" % evt[2], "a")
    
    logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + "← " + evt[0][1:].split("!")[0] + " est parti du canal")
    if len(evt)>=4:
        logFile.write("(raison: %s" % evt[3:][1:])
    logFile.write("\n")

    logFile.close()
