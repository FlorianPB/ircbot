#!/usr/bin/env python3
# -*- coding: utf8 -*-

import util.log
import util.cfg
import net.connect
import net.irc


def runOnce():
    """Runs the bot once"""
    cfg = util.cfg.load()

    logger = util.log.Log("bot.log", file_l=util.log.DEBUG, stdout_l=util.log.DEBUG, stderr_l=util.log.WARNING)
    logger.log("Started log", "init.bot", util.log.NOTIF)

    connectHandler = net.connect.Connect(logger.log, cfg["srv"], cfg["port"])
    connectHandler.start()
    logger.log("TCP Connection initialized", "init.bot", util.log.INFO)

    logger.log("IRC Server identication...", "init.bot", util.log.INFO)
    ircHandler = net.irc.IRC(cfg["nick"], connectHandler, logger.log, cfg["username"], cfg["realname"])
    ircHandler.ident()

    for chan in cfg["channels"]:
        ircHandler.join(chan)

    dontStop = True

    logger.log("IRC Server identication...", "init.bot", util.log.INFO)
    try:
        while dontStop:
            ircHandler.event(connectHandler.waitText())
    except:
        ircHandler.quit()
        connectHandler.stop()
        logger.log("Stopped the bot. Bye!", "init.bot", util.log.NOTIF)


runOnce()