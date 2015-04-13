#!/usr/bin/env python3
# -*- coding: utf8 -*-
import signal
import time

import util.log
import util.cfg
import util.exceptions
import util.modules
import net.connect
import net.irc


def runOnce():
    """Runs the bot once"""

    # Try to catch ctrl-C sigint signal.
    # Unfortunately, it doesn's want to work (even with a nice try… except: it's no use :/)
    dontStop = True

    def sigHandler(a, b):
        dontStop = False

    signal.signal(signal.SIGINT, sigHandler)

    cfg = util.cfg.load()

    # Start the logger utility, to tell the user what we are secretly doing behind his back.
    logger = util.log.Log("log/bot.log", file_l=util.log.DEBUG, stdout_l=util.log.DEBUG, stderr_l=util.log.WARNING)
    logger.log("Started log", "init.bot", util.log.NOTIF)

    # Start the connection handler to the configured server. We are basically saying hello to their machine ^^
    connectHandler = net.connect.Connect(logger.log, cfg["srv"], cfg["port"])
    connectHandler.start()
    logger.log("TCP Connection initialized", "init.bot", util.log.INFO)

    # Now we need to tell to the IRC server who we pretend to be.
    logger.log("IRC Server identication...", "init.bot", util.log.INFO)
    ircHandler = net.irc.IRC(cfg["nick"], connectHandler, logger.log, cfg["username"], cfg["realname"])
    ircHandler.hooks = {"JOIN":[], "PART":[], "QUIT":[], "PRIVMSG":[], "NICK":[], "MODE":[], "NOTICE":[]}
    ircHandler.ident()

    # Load all our little dynamic modules, to do a lot of great stuff without tinkering in here directly
    util.modules.loadAllModules({"irc":ircHandler, "log":logger.log, "connect":connectHandler, "modules":util.modules})

    for chan in cfg["channels"]:
        ircHandler.join(chan)


    # Now we are logged and we have set up some channels to talk into, we start the main event loop.
    logger.log("IRC Server identication...", "init.bot", util.log.INFO)
    try:
        while True:
            ircHandler.event(connectHandler.waitText())
    except util.exceptions.StopException as e:
        logger.log("Stop asked: %s" % e.args[0], "init.bot", util.log.WARNING)

    # Theorically, sigHandler should set dontStop to False for us.
    # Practically, it doesn's do anything useful and python is simply killed of when ctlr-c'ing :(
    ircHandler.quit()

    connectHandler.stop()
    logger.log("Stopped the bot. Bye!", "init.bot", util.log.NOTIF)


runOnce()
