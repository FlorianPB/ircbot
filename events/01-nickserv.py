#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identify to nickserv if needed"""

bot = None

def init(botInstance):
    global bot

    bot = botInstance
    bot.irc.hooks["NOTICE"].append(nickservIdent)

def nickservIdent(evt):
    """Get nickserv password"""
    evt[0].lower() == ":nickserv!nickserv@services."
    if " ".join(evt[3:7]).lower() == ":this nickname is registered." and not bot.cfg["serverpass"]:
        pw = input(bot._("NickServ password for ") + evt[2] + " : ")
        bot.connect.sendText("PRIVMSG NickServ :IDENTIFY " + pw + "\r\n")
        del pw

    if " ".join(evt[3:7]).lower() == ":you are now identified" and bot.cfg["waitNickserv"]:
        bot.identified = True
