#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import util.log

bot = None

class IRC:
    """IRC basic methods"""

    def __init__(self, botInstance):
        global bot
        self.chans = {}
        self.hooks = {"JOIN": [], "PART": [], "QUIT": [], "PRIVMSG":[], "NICK":[], "MODE": [], "NOTICE": []}

        bot = botInstance

    def ident(self):
        """Identifies at the beginning of the connection (send USER and NICK commands)"""
        # Send user info
        bot.status.status(message="Sending ident info")
        bot.connect.sendText("USER %s a a :%s\r\n" % (bot.cfg["username"], bot.cfg["realname"]))
        if bot.cfg["serverpass"]:
            pw = input("Server password: ")
            bot.connect.sendText("PASS %s:%s\r\n" % (bot.cfg["username"], pw))
            del pw
        bot.status.status(bot.status.OK, True)

        # Send nick info
        bot.status.status(bot.status.OK, True, "Sending nickname")
        bot.connect.sendText("NICK %s\r\n" % bot.cfg["nick"])

    def join(self, chan):
        """Joins a channel if we aren't already in it"""
        bot.status.status(message="Joining " + chan)
        if not self.chans.__contains__(chan):
            if chan != "/dev/console":
                bot.connect.sendText("JOIN %s\r\n" % chan)
            self.chans[chan] = {}
        bot.status.status(bot.status.OK, True)

    def part(self, chan, partMessage="Bye bye !"):
        """Parts from a channel"""
        chan = chan.lower()
        if self.chans.__contains__(chan) and chan != "/dev/console":    # Don't part from system console, never do that!
            if chan != "/dev/console":
                bot.connect.sendText("PART %s :\"%s\"\r\n" % (chan, partMessage))
            
            del self.chans[chan]

    def quit(self, partMessage="Bye bye !"):
        """Parts from the server"""
        from time import sleep

        c = list(self.chans.keys())
        for chan in c:
             self.part(chan, partMessage)

        bot.connect.sendText("QUIT\r\n")

    def msg(self, message, dest):
        """Sends a message
        message: the text to send
        dest: the target (#channel or nick)"""
        from time import strftime, sleep

        # Output log target
        if dest[0] == "#":
            logFile = open("log/" + dest + ".log", "a")
        elif dest == "/dev/console":
            logFile = open("log/consoleChan.log", "a")
        else:
            logFile = open("log/" + bot.cfg["nick"] + ".log", "a")

        # Write to log whether it's and action (prefix nickname with '*') or a user message (no prefix)
        if message[0:7] == "\x01ACTION":
            logLine = "*" + bot.cfg["nick"] + " " + message[8:].replace("\x01", "")
        else:
            logLine = "<" + bot.cfg["nick"] + ">" + message
        logFile.write(strftime("[%Y-%m-%d %H:%M:%S]") + logLine + "\n")

        logFile.close()

        # If target is /dev/console, print message to stdout or else send it to irc server
        if dest == "/dev/console":
            print("<" + bot.cfg["nick"] + "> " + message)
        else:
            # Cuts long messages if they are larger than 256 caracters
            while len(message) > 256:
                bot.connect.sendText("PRIVMSG " + dest + " :" + message[0:256] + "\r\n")
                message = message[256:]
                sleep(0.1)

            bot.connect.sendText("PRIVMSG " + dest + " :" + message + "\r\n")

    def event(self, ircLine):
        """Executes event line"""

        # Transforms the buffer into UNIX line endings to ease the line splitting
        ircLine = ircLine.replace("\r", "\n").replace("\n\n", "\n").replace("\xA0", " ")

        # If we get multiple lines at once, treat them separately
        # (plus it allows us to automatically strip the useless \n ending each line! yay!)
        for line in ircLine.split("\n"):
            if line != '':  # Don't treat empty event line
                evt = line.split()

                # Answer to pings (important, to not be kicked out for ping timeout)
                bot.log.log(bot._("Got event line: %s") % line, "net.irc.event", util.log.DEBUG)
                if evt[0] == "PING":
                    bot.log.log(bot._("Got pinged !"), "net.irc.event", util.log.INFO)
                    bot.connect.sendText("PONG " + evt[1][1:] + " " + evt[1] + "\r\n")

                # For each event, call the hooks corresponding to the command in evt[1] (JOIN, PRIVMSG etc, the event identifier)
                # Passing irc obj reference, event line splitted
                if len(evt)>=2 and self.hooks.__contains__(evt[1]):
                    bot.log.log(bot._("Looking for hooks for registered event %s") % evt[1], "net.irc.event", util.log.DEBUG)
                    for hook in self.hooks[evt[1]]:
                        bot.log.log(bot._("Running hook function %s.%s against this event") % (hook.__module__, hook.__name__), "net.irc.event", util.log.DEBUG)
                        hook(evt)
