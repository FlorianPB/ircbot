#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: foldlevel=1

from os import chdir, getcwd
from os.path import dirname
from sys import path

path.insert(1, dirname(__file__))

import gettext
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

        self.log = util.log.Log("log/bot.log", file_l=util.log.DEBUG, stdout_l=util.log.INFO, stderr_l=util.log.WARNING)
        self.connect = net.connect.Connect(self)
        self.irc = net.irc.IRC(self)

        # Gettext localisation
        self.t = gettext.translation("ircbot", getcwd()+"/locale")
        self._ = self.t.gettext

        # Set state booleans
        self.isRunning = False
        self.consoleRunning = True
        self.joined = False
        self.identified = not self.cfg["waitNickserv"] # if we have to wait nickserv, set identified to False at startup.

        # Add console channel to available channels, to allow modules to be able to recognize it
        # as a valid channel
        self.irc.join("/dev/console")

    def start(self):
        """Start the connection, the irc instance, load the modules"""
        if self.isRunning:
            # Already running, quit!!
            return

        self.joined = False
        self.identified = not self.cfg["waitNickserv"] # if we have to wait nickserv, set identified to False at startup.

        self.log.log(self._("Starting log"), "ircbot", util.log.NOTIF)
        self.connect.start()
        self.irc.ident()
        self.modules.loadAllModules(self)

        self.isRunning = True

    def joinAll(self):
        # Opening all our chat channels
        for chan in self.cfg["channels"]:
            self.irc.join(chan)

        self.joined = True

    def ircEventLoop(self):
        """Main bot Event loop"""

        while self.isRunning:
            # We just identified. Join all chans !
            if self.identified and not self.joined:
                self.joinAll()

            self.irc.event(self.connect.checkText())
            time.sleep(0.1)

    def consoleEventLoop(self):
        """System console events"""
        while self.consoleRunning:
            # If irc connection is active, we wait till the joins.
            # If not, we can continue, there is nothing to wait for.
            if (self.isRunning and self.identified and self.joined) or (not self.isRunning and self.consoleRunning):
                self.irc.event(":admin!~admin@localhost PRIVMSG /dev/console :" + str(input("<admin> ")) + "\r\n")
            time.sleep(0.1)

    def stop(self):
        self.irc.quit()
        self.connect.stop()
        self.isRunning = False
        self.joined = False

def run():
    """Starts the bot"""
    chdir(dirname(__file__))
    bot = IRCBot()
    
    console = threading.Thread(None, bot.consoleEventLoop)
    bot.start()
    console.start()
    
    try:
        while True:
            # While console is running, wait because user could want to start again the bot's connection
            if bot.isRunning:
                bot.ircEventLoop()
            else:
                bot.stop()
                bot.start()
                time.sleep(1)
    except:
        pass

    console.join()

if __name__=="__main__":
    run()
