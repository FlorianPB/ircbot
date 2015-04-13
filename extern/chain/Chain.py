# lastNick = ""

# net.irc.event
# │ if botLastMsg[nick] > 0 and nick!=lastNick:
# │ │   lastNick = nick
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
