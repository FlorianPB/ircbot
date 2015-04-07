#!/usr/bin/env python3
# -*- coding: utf8 -*-

import util.log

class IRC:
    """IRC basic methods"""

    def __init__(self, nick, sendTextMethod, waitTextMethod, logMethod, username="IRCBot", realname="IRC Python bot"):
        self.chans = {}
        self.hooks = {"JOIN":[], "PART":[], "PRIVMSG":[], "PING":[]}
        self.nick = nick
        self.username = username
        self.realname = realname

        self.send = sendTextMethod
        self.wait = waitTextMethod
        self.log = logMethod

    def ident(self):
        """Identifies at the beginning of the connection (send USER and NICK commands)"""
        self.send("USER %s a a :%s\r\n" % (self.username, self.realname))
        self.log(self.wait(), "net.irc.ident", util.log.DEBUG)

        self.send("NICK %s\r\n" % self.nickname)
        self.log(self.wait(), "net.irc.ident", util.log.DEBUG)

        # TODO: check if NickServ asks for a password

    def join(self, chan):
        """Joins a channel if we aren't already in it"""
        if not self.chans.keys().__contains__(chan):
            self.send("JOIN %s\r\n" % chan)
            self.log(self.wait(), "net.irc.join", util.log.DEBUG)

            self.chans[chan] = {"log": [], "eventFifo": []}

        # If we already joined... do nothing more :]

    def part(self, chan, partMessage="Bye bye !"):
        """Parts from a channel"""
        if self.chans.keys().__contains__(chan):
            self.send("PART %s :%s\r\n" % (chan, partMessage))
            self.log(self.wait(), "net.irc.part", util.log.DEBUG)

            # self.writeLog(chan)
            del self.chans[chan]

    def quit(self, partMessage="Bye bye !"):
        """Parts from the server"""
        for chan in self.chans.keys():
            self.part(chan, partMessage)
        self.send("QUIT\r\n")

    def event(self, ircLine):
        """Executes event line"""
        evt = ircLine.split()

        # For each event, call the hooks corresponding to the command in event[1] (JOIN, PRIVMSG etc)
        # Passing irc obj reference, event line splitted
        if self.hooks.__contains__(evt[1]):
            for i in self.hooks[evt[1]]:
                i(self, evt)
