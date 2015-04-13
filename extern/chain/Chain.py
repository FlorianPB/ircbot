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
# └─┴───run chainTrigger to check to either answer something or register it for future answer to be built

# chainTrigger
# │ create chain from stack[nick]
# │ 
# │ while no reaction found and chain not empty:
# │ │   search trigger for chain
# │ │
# │ │   if none found for this chain:
# │ │   │   discard oldest item
# │ │   else:
# │ │   │   outputs reaction (call net.irc.msg)
# │ │   │   run actions if any (identified in the chain by an ID or a tag)
# │ └───┴───refresh stack[nick] with found reaction add trigger
# │ if no reaction found:
# └─┴───put full chain in pendingStack[nick] to be added later by dev

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
# chainTrigger
# { "pattern": { "name": "chainTriggerName", "msg": "msgText" } }

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
        self.chainTriggers = util.cfg.load("chainTriggers.json")
        self.pendingStack = util.cfg.load("pendingStack.json")

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
        chain = self.stack[nick]
        reaction = False
        
        while (not reaction) and len(chain)>0:
            for chainTrigger in self.chainTriggers.keys():
                if re.search(chainTrigger, ":".join(chain)) != None:
                    initData["irc"].msg(nick + ": " + )
                    stack[nick] = chain + [chainTrigger]
                    reaction = True
                else:
                    if len(chain)>1:
                        chain = chain[1:]
                    else:
                        chain = []

        if not reaction:
            self.pendingStack[nick].append((stack[nick],""))
            util.cfg.save(self.pendingStack, "pendingStack.json")

    def joinHook(evt):
        nick = evt[0][1:].split("!")[0]
        self.stack[nick] = []
        self.botLastMsg[nick] = 2

    def partHook(evt):
        nick = evt[0][1:].split("!")[0]
        del self.stack[nick]

# Move that to events/xx-chainedTriggers.py
initData = {}
chainTrg = None

def init(data):
    global initData, chainTrg

    initData = data
    chainTrg = ChainTrigger(initData["cfg"]["nickRegexp"])

    initData["irc"].hooks["PRIVMSG"].append(chainTrg.msgTrigger)
    initData["irc"].hooks["JOIN"].append(chainTrg.joinHook)
    initData["irc"].hooks["PART"].append(chainTrg.partHook)
    initData["irc"].hooks["QUIT"].append(chainTrg.partHook)
