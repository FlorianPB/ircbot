#!usr/bin/env python3
# -*- coding: utf8 -*-

import importlib
import os

import util.log

modules={}

def loadAllModules(data, logFunc):
    """Load every module"""
    files = os.listdir("events")
    
    # Empty previously set up hooks
    for hookName in data["irc"].hooks.keys():
        data["irc"].hooks[hookName] = []

    modules = {}

    for moduleFile in files:
        moduleNameLen = len(moduleFile)
        moduleName = moduleFile[0:moduleNameLen-3]

        # Load every file ending in *.py into the dictionnary, associating it's code with it's name
        if moduleFile[moduleNameLen-3:moduleNameLen] == ".py":
            logFunc("Loading %s…" % moduleName, "util.modules", util.log.INFO)
            modules[moduleName] = importlib.import_module("events." + moduleName)

            logFunc("Initializing module…", "util.modules", util.log.INFO)
            # Initializing module, mainly setting up hooks
            modules[moduleName].init(data)
