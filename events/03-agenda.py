#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lists events"""

import os, time

bot = None
events = []
path = "events.lst"

def init(botInstance):
    """Inits the module"""
    global bot

    bot = botInstance
    load()

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdEvent, "event")
    bot.irc.hooks["JOIN"].append(checkEvent)

def load():
    global events
    if os.path.exists(path):
        with open(path, "rb") as f:
            events = f.read().decode().split("\n")
        events = [i for i in events if len(i)>0]

def cmdEvent(data, opts=[]):
    """event command.
    event list: list all upcoming events with their date and description"""
    if len(opts)<1:
        bot.irc.msg("Hey, I need some parameters!", data["tgt"])
        return

    load()
    
    if opts[0] == "list":
        now = int(time.mktime(time.localtime()))
        nextEvents = 0
        for event in events:
            t = int(event.split()[0])
            if t > now:
                nextEvents += 1
                bot.irc.msg(time.strftime("[%F %T]: ", time.localtime(t)) + " ".join(event.split()[1:]), data["tgt"])

        if nextEvents == 0:
            bot.irc.msg("Sorry, no upcoming event :/", data["tgt"])

def checkEvent(evt):
    """Tells the next upcoming event"""
    load()

    userName = evt[0].split("!")[0][1:]
    channel = evt[2]
    now = int(time.mktime(time.localtime()))

    nextEventId = -1
    nextEvent = ""

    for event in events:
        t = int(event.split()[0])
        if t>now and nextEventId>t:
            nextEventId = t
            nextEvent = event
        elif nextEventId<0 and t>now:
            nextEventId = t
            nextEvent = event

    if nextEventId>0:
        bot.irc.msg(userName + ", " + " ".join(nextEvent.split()[1:]) + " le " + time.strftime("%A %d %B %Y à %R", time.localtime(nextEventId)), channel)
