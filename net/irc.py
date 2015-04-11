#!/usr/bin/env python3
# -*- coding: utf8 -*-

import util.log

class IRC:
    """IRC basic methods"""

    def __init__(self, nick, connection, logMethod, username="IRCBot", realname="IRC Python bot"):
        self.chans = {}
        self.hooks = {}
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

        # TODO: check if NickServ asks for a password (yes, I didn't code that already)

    def join(self, chan):
        """Joins a channel if we aren't already in it"""
        if not self.chans.__contains__(chan):
            self.connection.sendText("JOIN %s\r\n" % chan)
            self.log(self.connection.waitText(), "net.irc.join", util.log.DEBUG)

            self.chans[chan] = {}

        # If we already joined... do nothing more :]

    def part(self, chan, partMessage="Bye bye !"):
        """Parts from a channel"""
        if self.chans.__contains__(chan):
            self.connection.sendText("PART %s :\"%s\"\r\n" % (chan, partMessage))
            self.log(self.connection.waitText(), "net.irc.part", util.log.DEBUG)
            
            del self.chans[chan]

    def quit(self, partMessage="Bye bye !"):
        """Parts from the server"""
        from time import sleep

        c = list(self.chans.keys())
        for chan in c:
            self.part(chan, partMessage)

        self.connection.sendText("QUIT\r\n")

    def msg(self, message, dest):
        """Sends a message
        message: the text to send
        dest: the target (#channel or nick)"""
        from time import strftime

        if dest[0] == "#":
            logFile = open(dest + ".log", "a")
        else:
            logFile = open(self.nick + ".log", "a")

        if message[0:7] == "\x01ACTION":
            logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " * " + self.nick + " " + message[8:].replace("\x01", "") + "\n")
        else:
            logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + " <" + self.nick + "> " + message + "\n")

        logFile.close()
        self.connection.sendText("PRIVMSG " + dest + " :" + message + "\r\n")


    def event(self, ircLine):
        """Executes event line"""

        # Transforms the buffer into UNIX line endings to ease the line splitting
        ircLine = ircLine.replace("\r", "\n").replace("\n\n", "\n")

        # If we get multiple lines at once, treat them separately
        # (plus it allows us to automatically strip the useless \n ending each line! yay!)
        for line in ircLine.split("\n"):
            if line != '':  # Don't treat empty event line
                evt = line.split()

                # Answer to pings (important, to not be kicked out for ping timeout)
                self.log("Got event line: %s" % line, "net.irc.event", util.log.DEBUG)
                if evt[0] == "PING":
                    self.log("Got pinged !", "net.irc.event", util.log.INFO)
                    self.connection.sendText("PONG " + evt[1][1:] + " " + evt[1] + "\r\n")

                # For each event, call the hooks corresponding to the command in evt[1] (JOIN, PRIVMSG etc, the event identifier)
                # Passing irc obj reference, event line splitted
                if len(evt)>=2 and self.hooks.__contains__(evt[1]):
                    self.log("Looking for hooks for registered event %s" % evt[1], "net.irc.event", util.log.DEBUG)
                    for i in self.hooks[evt[1]]:
                        self.log("Running hook function %s.%s against this event" % (i.__module__, i.__name__), "net.irc.event", util.log.DEBUG)
                        i(evt)
