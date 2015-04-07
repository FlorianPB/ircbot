#!/usr/bin/env python3
# -*- coding: utf8 -*-

import util.log

class IRC:
    """IRC basic methods"""

    def __init__(self, nick, connection, logMethod, username="IRCBot", realname="IRC Python bot"):
        self.chans = {}
        self.hooks = {"JOIN":[], "PART":[], "PRIVMSG":[], "PING":[]}
        self.nick = nick
        self.username = username
        self.realname = realname

        self.connection = connection
        self.log = logMethod

    def ident(self):
        """Identifies at the beginning of the connection (send USER and NICK commands)"""
        self.connection.sendText("USER %s a a :%s\r\n" % (self.username, self.realname))
        self.log(self.connection.waitText(), "net.irc.ident", util.log.DEBUG)

        self.connection.sendText("NICK %s\r\n" % self.nick)
        self.log(self.connection.waitText(), "net.irc.ident", util.log.DEBUG)

        # TODO: check if NickServ asks for a password

    def join(self, chan):
        """Joins a channel if we aren't already in it"""
        if not self.chans.keys().__contains__(chan):
            self.connection.sendText("JOIN %s\r\n" % chan)
            self.log(self.connection.waitText(), "net.irc.join", util.log.DEBUG)

            self.chans[chan] = {"log": [], "eventFifo": []}

        # If we already joined... do nothing more :]

    def part(self, chan, partMessage="Bye bye !"):
        """Parts from a channel"""
        if self.chans.keys().__contains__(chan):
            self.connection.sendText("PART %s :%s\r\n" % (chan, partMessage))
            self.log(self.connection.waitText(), "net.irc.part", util.log.DEBUG)

            # self.writeLog(chan)

    def quit(self, partMessage="Bye bye !"):
        """Parts from the server"""
        for chan in self.chans.keys():
            self.part(chan, partMessage)
        self.send("QUIT\r\n")

    def event(self, ircLine):
        """Executes event line"""

        # Transforms the buffer into UNIX line endings to ease the line splitting
        ircLine = ircLine.replace("\r", "")

        # If we get multiple lines at once, treat them separately
        # (plus it allows us to automatically strip the useless \n ending each line! yay!)
        for line in ircLine.split("\n"):
            if line != '':  # Don't treat empty event line
                evt = line.split()

                # For each event, call the hooks corresponding to the command in event[1] (JOIN, PRIVMSG etc, the event identifier)
                # Passing irc obj reference, event line splitted

                self.log("Got event line: %s" % ircLine, "init.bot", util.log.DEBUG)
                if self.hooks.__contains__(evt[1]):
                    self.log("Looking for hooks for event %s" % evt[1], "init.bot", util.log.DEBUG)
                    for i in self.hooks[evt[1]]:
                        self.log("Running hook function against this event", "init.log", util.log.DEBUG)
                        i(self, evt)
