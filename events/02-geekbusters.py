#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module description"""

import re
import time
import util.cfg

bot = None
naughtyBoys={}
wordList=["informatique", "linux", "pc", "install", "windows", "pam", "ordi", "ssd", "win7", "win8", "win10", "w7", "emerge", "portage", "gentoo", "archlinux", "bsod", "vm"]

def init(botInstance):
    """Inits the module"""
    global bot, naughtyBoys, wordList

    bot = botInstance
    util.cfg.default = naughtyBoys
    naughtyBoys = util.cfg.load("cfg/naughtyBoysList.json")
    util.cfg.default = wordList
    wordList = util.cfg.load("cfg/geekwordlist.json")

    reg = bot.modules.modules["01-simpleCommand"].registerCommand

    reg(cmdAddWord, "addWord", [":[^!]*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)", ":Shinsaber!~Shinsaber@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"] )
    reg(cmdClearUser, "clearUser", [":[^!]*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)", ":Shinsaber!~Shinsaber@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"] )
    reg(cmdShowList, "showList")
    reg(cmdShowStat, "showStat")
    bot.irc.hooks["PRIVMSG"].append(checkMsg)

def cmdAddWord(data, opts=[]):
    """Adds a word to the geekbuster list.
    addWord word [word […]]"""
    global wordList

    while len(opts) > 0:
        wordList.append(opts.pop())
    util.cfg.save(wordList, "cfg/geekwordlist.json")

def cmdShowList(data, opts=[]):
    """List current blacklisted words"""
    wordList = util.cfg.load("cfg/geekwordlist.json")
    bot.irc.msg(" ".join(wordList), data["tgt"])

def cmdShowStat(data, opts=[]):
    """List statistics for user.
    showStat [user1 [user2 […]]]"""
    naughtyBoysList = util.cfg.load("cfg/naughtyBoysList.json")
    if len(opts) == 0:
        for boy in naughtyBoys:
            bot.irc.msg("{u}: {n} strikes jusqu'ici.".format(u=boy, n=naughtyBoys[boy]["strikes"]), data["tgt"])

    while len(opts)>0:
        boy = opts.pop()
        if naughtyBoys.__contains__(boy):
            bot.irc.msg("{u}: {n} strikes jusqu'ici.".format(u=boy, n=naughtyBoys[boy]["strikes"]), data["tgt"])
        else:
            bot.irc.msg("{u} a été sage !".format(u=boy), data["tgt"])

def cmdClearUser(data, opts=[]):
    """Clear user from the naughty boy's list
    clearUser user1 [user2 […]]"""
    global naughtyBoys

    while len(opts)>0:
        del naughtyBoys[opts.pop()]
    util.cfg.save(naughtyBoys, "cfg/naughtyBoysList.json")

def checkMsg(evt):
    """Check user messages for things that shouldn't be here"""
    global naughtyBoys

    wordList = util.cfg.load("cfg/geekwordlist.json")
    naughtyBoysList = util.cfg.load("cfg/naughtyBoysList.json")

    user = evt[0][1:].split("!")[0]
    tgt = evt[2]
    txt = (" ".join(evt[3:])[1:]).lower()

    if tgt==bot.cfg["nick"]:
        tgt = user

    if tgt != "#bronycub":
        return

    txt = re.findall("([\w]*)\W*", txt)[:-1]
    for word in wordList:
        if txt.__contains__(word):
            if naughtyBoys.__contains__(user):
                naughtyBoys[user]["current"]+=txt.count(word)
            else:
                naughtyBoys[user]={"current":txt.count(word), "strikes":0, "lastStrike":0}
   
    # 3 words ? strike.
    if naughtyBoys.__contains__(user) and naughtyBoys[user]["current"] >= 3:
        bot.irc.msg("{u} : Ce n'est pas le chan pour parler de ceci. Je te prie d'aller sur #bronycub-g33k".format(u=user), tgt)
        bot.connect.sendText("INVITE " + user + " #bronycub-g33k\r\n")
        naughtyBoys[user]["current"]=0

        # Not stroke in the last 3 days ? Remove a strike (don't count this one)
        if naughtyBoys[user].__contains__("strikes"):
            if naughtyBoys[user].__contains__("lastStrike") and naughtyBoys[user]["lastStrike"] + (86400*3) > int(time.strftime("%s")):
                naughtyBoys[user]["strikes"]+=1
        else:
            naughtyBoys[user]["strikes"]=1
        
        # Last strike is *NOW*
        naughtyBoys[user]["lastStrike"] = int(time.strftime("%s"))

        # 9 strikes (3 kicks) ? you're banned.
        if naughtyBoys[user]["strikes"]%9 == 0 and naughtyBoys[user]["strikes"]>0:
            bot.connect.sendText("MODE #bronycub +b :" + user + "!*@*\r\n")
        
        # 3 strikes ? get out.
        if naughtyBoys[user]["strikes"]%3 == 0 and naughtyBoys[user]["strikes"]>0:
            bot.connect.sendText("KICK #bronycub " + user + " :Ce canal n'est pas là pour discuter d'informatique. Merci.\r\n")
        

    util.cfg.save(naughtyBoys, "cfg/naughtyBoysList.json")
