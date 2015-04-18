#!/usr/bin/env python3
# -*- coding: utf8 -*-

# net.irc.event
# │ if botLastMsg[nick] > 0:
# │ └───botLastMsg[nick]--
# └─run msgTrigger

# msgTrigger
# │ on trigger:
# │ └───append trigger to trigger stack
# │
# │ if botLastMsg[nick]>0 or message contains own's name:
# │ │   if no trigger found for user message:
# │ │   └───put user message and current stack[nick] to pendingStack[nick]
# └─┴───run chainTriggerTree to check to either answer something or register it for future answer to be built

# chainTriggerTree
# │ set current dbTree pos to root node
# │ set chain path to empty string
# │
# │ for each item in reverse stack[nick]:
# │ │   if current dbTree pos contains item:
# │ │   │   prepend item to chain path
# │ │   │   set current dbTree pos to newly found item
# │ │   else:
# │ └───┴───stop searching in stack
# │
# │ if chain path not empty:
# │ │   output current dbTree pos corresponding message
# │ │   run corresponding action id's action
# │ │   set stack[nick] to splitted chain path
# │ │   append dbTree pos chainTrigger name to stack[name]
# │ else:
# └─┴───put jointed stack to pendingStack[nick] to be added later

# net.irc.msg
# └─botLastMsg[nick] = 2

# event JOIN
# │ stack[nick] = []
# │ botLastMsg[nick] = 2

# event PART / QUIT
# │ del stack[nick]


# Ideas:
# - replace full trigger system
# - write / load pendingStacks to disk
# - add bot name's regular expression in cfg.json (ie for Berry-Punch: '[bB]erry([ -][pP]unch)?')
# - append user nick on each answer message for better clarity
# - use the chain trigger action for sending mails, for example to warn about certains behaviours (person being sad / depressed / etc..)

# File formats:
# trigger
# { "name": "pattern" }
# chainTrigger !! in reverse order, i.e. last triggered at root of the tree
# {
#   "name": "rootNode",
#   "trg": {
#       "trigger": {
#           "name": "chainTrigger name"
#           "msg": "msgText",
#           "trg": {
#               subchains goes here
#           }
#       }
#   }
# }

import re

import util.cfg

class ChainTrigger:
    def __init__(self, botPattern):
        util.cfg.default = {}
        self.botLastMsg = {}
        self.stack = {}
        self.botPattern = botPattern

        #  Loading triggers and pending stuff 
        self.triggers = util.cfg.load("triggers.json")
        self.pendingStack = util.cfg.load("pendingStack.json")

        util.cfg.default = {"name": "root", "trg":{}}
        self.chainTriggers = util.cfg.load("chainTriggers.json")

    def msgTrigger(self, evt):
        """net.irc.event hook function"""
        text = " ".join(evt[3:])[1:]
        nick = evt[0][1:].split("!")[0]
        triggerFound = False

        for trigger in self.triggers.keys():
            if re.search(self.triggers[trigger], text) != None:
                self.stack.append(trigger)
                triggerFound = True
        
        if self.botLastMsg[nick]>0 or re.search(self.botPattern, text) != None:
            if not triggerFound:
                self.pendingStack[nick].append((":".join(stack), text))
                util.cfg.save(self.pendingStack, "pendingStack.json")
            self.chainTrigger(nick)

    def chainTrigger(nick):
        treePos = self.chainTriggers
        chainPath = ""
        
        if not pendingStack.__contains__(nick):
            pendingStack[nick] = []

        # Get last item of chat first, to be able to contextually answer to trigger
        stack = self.stack[nick]
        stack.reverse()

        # Walk through stack, to find the deepest chain trigger available
        for trigger in stack:
            if treePos["trg"].__contains__(trigger):
                chainPath = trigger + ":" + chainPath
                treePos = treePos["trg"][trigger]
            else:
                # Even if we found something, if we couldn't apply the whole stack we add it there in case there will be something to improve.
                self.pendingStack[nick].append((":".join(self.stack[nick]), "")
                util.cfg.save(self.pendingStack, "pendingStack.json")
                break

        # If we have any matching, we print the message if any
        if chainPath != "":
            chainPath = chainPath[0:len(chainPath)-1]

            if treePos.__contains__("msg"):
                initData["irc"].msg(nick + ": " + treePos["msg"].replace("%user", nick))
            else:
                self.pendingStack[nick].append((chainPath, ""))
                util.cfg.save(self.pendingStack, "pendingStack.json")

            # Append our contribution to the stack, to 'remember' what we said
            stack[nick] = chainPath.split(":")
            stack[nick].append(treePos["name"])
        else:
            # Nothing found ? Add unwound stack to pending items, to be able to add it manually in the chainTrigger tree
            self.pendingStack[nick].append((":".join(self.stack[nick]), "")
            util.cfg.save(self.pendingStack, "pendingStack.json")

    def joinHook(evt):
        nick = evt[0][1:].split("!")[0]
        if not self.stack.__contains__(nick):
            self.stack[nick] = []
        self.botLastMsg[nick] = 2
        self.stack[nick].append("JOIN")

    def partHook(evt):
        nick = evt[0][1:].split("!")[0]
        self.stack[nick].append("PART")

# Move that to events/xx-chainedTriggers.py

bot = None
chainTrg = None

def init(botInstance):
    global bot, chainTrg

    bot = botInstance
    chainTrg = ChainTrigger(bot.cfg["nickRegexp"])

    bot.irc.hooks["PRIVMSG"].append(chainTrg.msgTrigger)
    bot.irc.hooks["JOIN"].append(chainTrg.joinHook)
    bot.irc.hooks["PART"].append(chainTrg.partHook)
    bot.irc.hooks["QUIT"].append(chainTrg.partHook)
