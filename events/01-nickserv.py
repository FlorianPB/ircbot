#!/usr/bin/env python3
# -*- codimg: utf8 -*-
"""Identify to nickserv if needed"""

initData = {}

def init(data):
    global initData

    initData = data
    data["irc"].hooks["NOTICE"].append(nickservIdent)

def nickservIdent(evt):
    """Get nickserv password"""
    evt[0].lower() == ":nickserv!nickserv@services."
    if " ".join(evt[3:7]).lower() == ":this nickname is registered.":
        pw = input("NickServ password for " + evt[2] + " : ")
        initData["connect"].sendText("PRIVMSG NickServ :IDENTIFY " + pw + "\r\n")
        del pw
