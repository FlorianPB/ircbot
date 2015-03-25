#!/usr/bin/env python3
# -*- coding: utf8 -*-

class IRC:
    """IRC basic methods"""

    def __init__(self, nick, username="IRCBot", realname="IRC Python bot"):
        self.chans = {}
        self.hooks = {"JOIN":[], "PART":[], "PRIVMSG":[], "PING":[]}
        self.nick = nick
        self.username = username
        self.realname = realname

    def ident(self):
        """Identifies at the beginning of the connection (send USER and NICK commands)"""
        # TODO: implement actual connection through existing tcp socket
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
        return self.chans[chan]["eventFifo"].pop()
