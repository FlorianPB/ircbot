#!/usr/bin/env python3
# -*- coding: utf8 -*-

from time import strftime
from sys import stdout,stderr

# Log levels
DEBUG    = 0
INFO     = 1
NOTIF    = 2
WARNING  = 3
ERROR    = 4
CRIRITAL = 5

textLevels = {
        0:"DEBUG",
        1:"INFOR",
        2:"NOTIF",
        3:" WARN",
        4:"ERROR",
        5:" CRIT"
}

class Log:
    """Log events to terminal and to a file on disk"""
    handle = None,
    path = "/tmp/ircbot.log"
    fileLogLevel   = INFO
    stdoutLogLevel = NOTIF
    stderrLogLevel = WARNING

    def __init__(self, fp, file_l=INFO, stdout_l=NOTIF, stderr_l=WARNING):
        """Initializes logger"""
        self.fileLogLevel   = file_l
        self.stdoutLogLevel = stdout_l
        self.stderrLogLevel = stderr_l
        self.path = fp

    def log(self, content, head="logger", level=INFO):
        """Outputs a log line"""

        strLog = "[%s] %s %s: %s\n" % (strftime("%Y-%m-%d %H:%M:%S"), textLevels[level], head, content)

        handle = open(self.path, "a")
        if level>=self.fileLogLevel:
            handle.write(strLog)
            handle.flush()
        
        if level>=self.stderrLogLevel:
            stderr.write(strLog)
            stderr.flush()
        elif level>=self.stdoutLogLevel:
            stdout.write(strLog)
            stdout.flush()
        handle.close()
