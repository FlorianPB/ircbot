#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vote system."""

bot = None

voteDesc   = ""
voteOpener = None
votes      = {}
choiceQty  = []
choiceDesc = []

def init(botInstance):
    """Inits the module"""
    global bot

    bot = botInstance

    bot.modules.modules["01-simpleCommand"].registerCommand(cmdAskVote, "askvote")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdAddChoice, "addchoice")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdVote, "vote")
    bot.modules.modules["01-simpleCommand"].registerCommand(cmdCloseVote, "closevote", [":.*!~adriens33@(2001:41[dD]0:[aA]:1308::1|homer\.art-software\.fr)"])
    # bot.irc.hooks["PRIVMSG"].append(hookThingy)

def cmdAskVote(data, opts=[]):
    """askvote <subject>
    Opens a vote."""
    global voteDesc, voteOpener, votes, choiceQty, choiceDesc

    if voteOpener != None:
        bot.irc.msg(bot._("A vote is already opened."), data["tgt"])
        return

    if len(opts)<1:
        bot.irc.msg(bot._("No description given."), data["tgt"])
        return
    
    voteDesc   = " ".join(opts)
    voteOpener = data["user"]
    votes      = {}
    choiceQty  = []
    choiceDesc = []
    bot.irc.msg(bot._("Vote opened."), data["tgt"])

def cmdAddChoice(data, opts=[]):
    """addchoice <choice description>
    Adds a choice in a vote."""
    global choiceQty, choiceDesc

    if len(opts)<1:
        bot.irc.msg(bot._("No description given."), data["tgt"])
        return
    
    choice = " ".join(opts)
    choiceDesc.append(choice)
    choiceQty.append(0)
    bot.irc.msg(bot._("Choice added at %d.") % len(choiceDesc), data["tgt"])

def cmdVote(data, opts=[]):
    """vote [id]
    Votes for a choice or display stats"""
    global votes, choiceQty

    if voteOpener == None:
        bot.irc.msg(bot._("No vote has been opened. See help askvote."), data["tgt"])
        return

    if len(opts)<1:
        bot.irc.msg(bot._("Vote from %s:") % voteOpener, data["tgt"])
        bot.irc.msg(voteDesc, data["tgt"])
        bot.irc.msg(bot._("Available choices :"), data["tgt"])
        for i, c in enumerate(choiceDesc):
            bot.irc.msg(str(i+1) + "/ " + c + " (" + str(choiceQty[i]) + " " + bot._("votes") + ")", data["tgt"])
    else:
        c = int(opts[0])
        if c>=1 and c<=len(choiceDesc):
            if votes.__contains__(data["user"]):
                bot.irc.msg(bot._("You already voted. Changing your vote to %d") % c, data["tgt"])
                choiceQty[votes[data["user"]]] -= 1
                choiceQty[c-1] += 1
                votes[data["user"]] = c-1
            else:
                bot.irc.msg(bot._("You voted for %d.") % c, data["tgt"])
                choiceQty[c-1] += 1
                votes[data["user"]] = c-1

def cmdCloseVote(data, opts=[]):
    """closevote
    Closes a running vote."""
    global voteDesc, voteOpener

    bot.irc.msg(bot._("%s's vote closed.") % voteOpener, data["tgt"])
    q = max(choiceQty)
    if choiceQty.count(q)==1:
        bot.irc.msg(bot._("Choice retained: %s") % choiceDesc[choiceQty.index(q)], data["tgt"])
    else:
        bot.irc.msg(bot._("Draw vote, no winner."))

    voteDesc=""
    voteOpener=None

# def hookThingy(evt):
#     """Does something on an event."""
