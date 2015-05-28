#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import randint
import re

import util.cfg

class Quizz:
    MODE_ONESHOT = 1
    MODE_REGULAR = 2
    MODE_PARTY   = 3

    def __init__(self, botName, channel, defaultMode=MODE_ONESHOT):
        util.cfg.default = {}
        self.questions = util.cfg.load("extern/quizz/questions.json")
        self.mode = defaultMode
        self.channel = channel
        self.activeQuestion = None

    def randomQuestion(self):
        """Get a random question"""
        self.activeQuestion = list(self.questions.keys())[randint(0,len(self.questions)-1)]
        return self.activeQuestion

    def checkAnswer(self, answer):
        """Verifies the answer to the active question"""
        if self.activeQuestion != None and re.search(self.questions[self.activeQuestion], answer) != None:
            self.activeQuestion = None
            return True

        return False

    def questionPending(self):
        """Is there a active question ?"""
        return self.activeQuestion != None

    def setQuestion(self, question, answerPattern=" "):
        """Saves the answer to a given question"""
        self.questions[question] = answerPattern
        util.cfg.save(self.questions, "extern/quizz/questions.json")
