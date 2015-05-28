#!usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import os

import util.log

modules={}

def loadAllModules(botInstance):
    """Load every module"""
    global modules

    files = os.listdir("events")
    files.sort()
    
    # Empty previously set up hooks
    for hookName in botInstance.irc.hooks.keys():
        botInstance.irc.hooks[hookName] = []

    modules = {}

    for moduleFile in files:
        moduleNameLen = len(moduleFile)
        moduleName = moduleFile[0:moduleNameLen-3]

        # Load every file ending in *.py into the dictionnary, associating it's code with it's name
        if moduleFile[moduleNameLen-3:moduleNameLen] == ".py":
            botInstance.log.log(botInstance._("Loading %s…") % moduleName, "util.modules", util.log.INFO)
            modules[moduleName] = importlib.import_module("events." + moduleName)

            # Show module Docstring
            botInstance.log.log(modules[moduleName].__doc__, "util.modules", util.log.INFO)

            # Initializing module, mainly setting up hooks
            botInstance.log.log(botInstance._("Initializing module…"), "util.modules", util.log.INFO)
            modules[moduleName].init(botInstance)
