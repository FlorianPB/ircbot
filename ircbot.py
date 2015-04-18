#!/usr/bin/env python3
# -*- coding: utf8 -*-

import threading
import time

import util.log
import util.cfg
import util.exceptions
import util.modules
import net.connect
import net.irc

class IRCBot:
    import util.modules as modules

    def __init__(self):
        """Initializes bot data"""
        self.cfg = util.cfg.load()

        self.log = util.log.Log("log/bot.log", file_l=util.log.DEBUG, stdout_l=util.log.NOTIF, stderr_l=util.log.WARNING)
        self.connect = net.connect.Connect(self.log.log, self.cfg["srv"], self.cfg["port"])

        self.irc = net.irc.IRC(self.cfg["nick"], self.connect, self.log.log, self.cfg["username"], self.cfg["realname"])
        self.irc.hooks = {"JOIN": [], "PART": [], "QUIT": [], "PRIVMSG":[], "NICK":[], "MODE": [], "NOTICE": []}
        self.isRunning = False
        self.joined = False
        self.identified = not self.cfg["waitNickserv"] # if we have to wait nickserv, set identified to False at startup.

    def start(self):
        """Start the connection, the irc instance, load the modules"""
        self.log.log("Starting log", "ircbot", util.log.NOTIF)
        self.connect.start()
        self.irc.ident()
        self.modules.loadAllModules(self)

        self.isRunning = True


    def joinAll(self):
        # Opening all our chat channels
        for chan in self.cfg["channels"]:
            self.irc.join(chan)

        # Add console channel to available channels, to allow modules to be able to recognize it
        # as a valid channel
        self.irc.join("/dev/console")

        self.joined = True

    def ircEventLoop(self):
        """Main bot Event loop"""

        while self.isRunning:
            # We just identified. Join all chans !
            if self.identified and not self.joined:
                self.joinAll()

            self.irc.event(self.connect.waitText())

    def consoleEventLoop(self):
        """System console events"""
        while self.isRunning:
            if self.identified and self.joined:
                self.irc.event(":admin!~admin@localhost PRIVMSG /dev/console :" + str(input("<admin> ")) + "\r\n")
            else:
                time.sleep(0.1)

    def stop(self):
        self.irc.quit()
        self.connect.stop()
        self.log.log("Bot has stopped. Bye !", "ircbot", util.log.NOTIF)
        self.isRunning = False


bot = IRCBot()
bot.start()

console = threading.Thread(None, bot.consoleEventLoop)
console.start()

while bot.isRunning:
    try:
        bot.ircEventLoop()
    except:
        import sys
        bot.log.log("Exception caught: %s, stopping  bot" % sys.exc_info().__str__(), "ircbot", util.log.WARNING)

bot.stop()
console.join()
