#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

default = {
        "srv":  "chat.freenode.net",
        "port": 6667,
        "channels":
            ["#testircbot"],
        "nick": "python_ircbot",
        "waitNickserv": False,
        "username": "pythonbot",
        "realname": "IRC Python bot by Art Software"
}

def save(cfgData, place="cfg/cfg.json"):
    """Saves current configuration into default cfg file
    cfgData: the dict containing the config
    place: the .json file path (default: cfg/cfg.json)"""

    with open(place, "w") as cfgFile:
        json.dump(cfgData, cfgFile)

def load(place="cfg/cfg.json"):
    """Loads cfg from file
    place: the .json file path (default: cfg/cfg.json)"""

    if os.path.exists(place):
        with open(place, "r") as cfgFile:
            cfgData = json.load(cfgFile)
    else:
        # No file ? Ok, create a shiny new file with default content ! :D
        cfgData = default
        save(cfgData, place)
    return cfgData
