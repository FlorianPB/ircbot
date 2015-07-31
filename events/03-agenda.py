#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lists events"""

import os, time

bot = None
events = []
path = "events.lst"
tellEvents = True
persons = {}

def init(botInstance):
    """Inits the module"""
    global bot

    bot = botInstance
    load()

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdEvent, "event")
    bot.irc.hooks["JOIN"].append(checkEvent)




def load():
    """Load event list"""
    global events
    now = int(time.mktime(time.localtime()))
    if os.path.exists(path):
        with open(path, "rb") as f:
            events = f.read().decode().split("\n")
        events = [i for i in events if len(i)>0 and int(i.split()[0])>now]
    update()

def update():
    """Write event list"""
    with open(path, "wb") as f:
        f.write(("\n".join(events)).encode("UTF-8"))




def cmdEvent(data, opts=[]):
    """event command.
    event list: list all upcoming events with their date and description
    event tell on/off: Whether to tell upcoming event to coming people
    event add YYYY-mm-dd HH:MM Description of the event"""
    global tellEvents, events

    if len(opts)<1:
        bot.irc.msg("Hey, I need some parameters!", data["tgt"])
        return

    load()
    
    if opts[0] == "tell":
        if len(opts)<2:
            return

        if opts[1] == "on":
            tellEvents = True
        elif opts[1] == "off":
            tellEvents = False

    elif opts[0] == "add":
        if len(opts)<3:
            return
        try:
            t = time.strftime("%s", time.strptime(" ".join(opts[1:3]), "%Y-%m-%d %H:%M"))
            events.append(t + " " + " ".join(opts[3:]))
            update()
        except:
            bot.irc.msg("Error: the event date '" + " ".join(opts[1:3]) + "' is not in the right format ! (YYYY-mm-dd HH:MM)", data["tgt"])

    elif opts[0] == "list":
        now = int(time.mktime(time.localtime()))
        nextEvents = 0
        for event in events:
            t = int(event.split()[0])
            if t > now:
                nextEvents += 1
                bot.irc.msg(time.strftime("[%F %R]: ", time.localtime(t)) + " ".join(event.split()[1:]), data["tgt"])

        if nextEvents == 0:
            bot.irc.msg("Sorry, no upcoming event :/", data["tgt"])





def checkEvent(evt):
    """Tells the next upcoming event"""
    global persons

    if not tellEvents:
        return

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
        if not persons.__contains__(userName) or persons[userName]<nextEventId:
            persons[userName] = nextEventId
            bot.irc.msg(userName + ", notre prochain événement: " + " ".join(nextEvent.split()[1:]) + " le " + time.strftime("%A %-d %B %Y à %-Hh%M", time.localtime(nextEventId)), channel)
