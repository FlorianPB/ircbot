#!/usr/bin/env python3
# -*- coding: utf8 -*-

import json
import os

default = {
        "srv":  "chat.freenode.net",
        "port": 6667,
        "channels":
            ["#testircbot"],
        "nick": "python_ircbot",
        "username": "pythonbot",
        "realname": "IRC Python bot by Art Software"
}

def save(cfgData, place="./cfg.json"):
    """Saves current configuration into default cfg file
    cfgData: the dict containing the config
    place: the .json file path (default: ./cfg.json)"""

    with open(place, "w") as cfgFile:
        json.dump(cfgFile, cfgData)

def load(place="./cfg.json"):
    """Loads cfg from file
    place: the .json file path (default: ./cfg.json)"""

    if os.path.exists(place):
        with open(place, "r") as cfgFile:
            cfgData = json.load(cfgFile)
    else:
        # No file ? Ok, create a shiny new file with default content ! :D
        cfgData = default
        save(cfgData, place)
