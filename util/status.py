#!/usr/bin/env python3
# -*- coding: utf-8 -*-

BUSY = 0
OK   = 1
FAIL = 2

__colors = {
        BUSY: 0b0100,
        OK:   0b1010,
        FAIL: 0b1001
}

__messages = {
        BUSY: "BUSY",
        OK:   " OK ",
        FAIL: "FAIL"
}

def status(statusType=BUSY, newLine=False, message=""):
    """Prints a status line.
    message: The message to display along the status (default: no (new) message)
    newline: If true, will print a newline to not update the current status line (default: False)
    type: Status type (default: BUSY)"""
    endLine = ["\r", "\n"][newLine] # Works since True ⇔ 1 and False ⇔ 0

    if len(message) > 0:
        message += "\x1B[0K"

    print(" [38;5;0;48;5;{c}m {s} [0m [1m{m}[0m".format(s=__messages[statusType], m=message, c=__colors[statusType]), end=endLine)
