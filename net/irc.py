#!/usr/bin/env python3
# -*- coding: utf8 -*-

import util.log

class IRC:
    """IRC basic methods"""

    def __init__(self, nick, sendTextMethod, waitTextMethol, logMethod, username="IRCBot", realname="IRC Python bot"):
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
            # TODO: Sends JOIN through the TCP socket
            self.chans[chan] = {"log": [], "eventFifo": []}

        # If we already joined... do nothing more :]

    def part(self, chan, partMessage="Bye bye !"):
        """Parts from a channel"""
        if self.chans.keys().__contains__(chan):
            # TODO: Sends PART through the TCP Socket
            self.writeLog(chan)
            del self.chans[chan]

    def quit(self, partMessage="Bye bye !"):
        """Parts from the server"""
        for chan in self.chans.keys():
            self.part(chan, partMessage)
        # TODO: Sends QUIT through the TCP socket

    def pushEvent(self, ircLine):
        """Push event line to the fifo"""
        evt = ircLine.split()
        self.chans[evt[2]]["eventFifo"].insert(0, [evt[0], evt[1], " ".join(evt[3:])])

    def popEvent(self, chan):
        """Pop event from the fifo"""

        while self.chans[chan]["eventFifo"].__len__() > 0:
            event = self.chans[chan]["eventFifo"].pop()

            # For each event, call the hooks corresponding to the command in event[1] (JOIN, PRIVMSG etc)
            # Passing source adress and eventual content
            if self.hooks.__contains__(event[1]):
                for i in self.hooks[event[1]]:
                    i(event[0], event[2])
