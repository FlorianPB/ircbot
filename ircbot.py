#!/usr/bin/env python3
# -*- coding: utf8 -*-

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

        self.log = util.log.Log("log/bot.log", file_l=util.log.DEBUG, stdout_l=util.log.INFO, stderr_l=util.log.WARNING)
        self.connect = net.connect.Connect(self.log.log, self.cfg["srv"], self.cfg["port"])

        self.irc = net.irc.IRC(self.cfg["nick"], self.connect, self.log.log, self.cfg["username"], self.cfg["realname"])
        self.irc.hooks = {"JOIN": [], "PART": [], "QUIT": [], "PRIVMSG":[], "NICK":[], "MODE": [], "NOTICE": []}

    def start(self):
        """Start the connection, the irc instance, load the modules"""
        self.log.log("Starting log", "ircbot", util.log.NOTIF)
        self.connect.start()
        self.irc.ident()
        self.modules.loadAllModules(self)

        # Opening all our chat channels
        for chan in self.cfg["channels"]:
            self.irc.join(chan)

    def eventLoop(self):
        """Main bot Event loop"""
        while True:
            self.irc.event(self.connect.waitText())

    def stop(self):
        self.irc.quit()
        self.connect.stop()
        self.log.log("Bot has stopped. Bye !", "ircbot", util.log.NOTIF)


bot = IRCBot()
bot.start()
try:
    bot.eventLoop()
except:
    import sys
    bot.log.log("Exception caught: %s, stopping  bot" % sys.exc_info().__str__(), "ircbot", util.log.WARNING)
    bot.stop()
