#!usr/bin/env python3
# -*- coding: utf8 -*-

import importlib
import os

import util.log

modules={}

def loadAllModules(data, logFunc):
    """Load every module"""
    files = os.listdir("events")
    
    for hook in data["irc"].hooks:
        hook = []

    for item in modules:
        item = None

    for moduleFile in files:
        moduleNameLen = len(moduleFile)
        moduleName = moduleFile[0:moduleNameLen-3]

        if moduleFile[moduleNameLen-3:moduleNameLen] == ".py":
            logFunc("Loading %s…" % moduleName, "util.modules", util.log.INFO)
            modules[moduleName] = importlib.import_module("events." + moduleName)

            logFunc("Initializing module…", "util.modules", util.log.INFO)
            modules[moduleName].init(data)
