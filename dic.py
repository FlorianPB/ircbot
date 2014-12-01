#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Author: Adrien Sohier
# Copyright © 2014, Art SoftWare
# 
# Depends:
# - python (noo, are you serious ? xD)
# - python-numpy

import json, os, time
from numpy import binary_repr

class WordDict:
    word_bin = {}
    bin_word = {}
    cur_index = 1
    file_path = "dict.json"

    def write_file(self):
        """Write dictionnary to a file"""
        data = {"word_bin":  self.word_bin,
                "bin_word":  self.bin_word,
                "cur_index": self.cur_index}
        with open(self.file_path, "w") as f:
            json.dump(data, f)

    def load_file(self):
        """Load the dictionnary from a file"""
        if os.path.isfile(self.file_path):
            with open(self.file_path, "r") as f:
                data = json.load(f)
            self.word_bin = data["word_bin"]
            self.bin_word = data["bin_word"]
            self.cur_index = data["cur_index"]
        else:
            word_bin = {}
            bin_word = {}
            cur_index = 1

    def add(self, word):
        """Adds a word to the dictionnary if it isn't already indexed
        word: the word to check / add"""
        if not self.word_bin.__contains__(word):
            binary_idx = binary_repr(self.cur_index, 16)

            self.word_bin[word] = binary_idx
            self.bin_word[binary_idx] = word
            self.cur_index += 1

    def cut(self, sentence):
        """Cut the words from a sentence
        sentence: the string to use to get the words"""

        return sentence.split(" ")

    def analyze(self, sentence):
        """Analyse a sentence and return an array containing the words' indexes
        (Automatically adds any unindexed word)"""
        indexes = []
        word_list = self.cut(sentence)

        self.load_file()
        for i in word_list:
            self.add(i)
            indexes += self.word_bin[i]
        self.write_file()

        return indexes

    def loop_fifo(self):
        """Loops on /tmp/brain-dic.<pid>.in and puts out on /tmp/brain-dic.<pid>.out
        Delete /tmp/brain-dic.pid to stop the loop"""
        pid = os.getpid()
        self.in_fifo_path = "/tmp/brain-dic.%d.in" % (pid)
        self.out_fifo_path = "/tmp/brain-dic.%d.out" % (pid)
        self.pid_file = "/tmp/brain-dic.pid"

        if os.path.exists(self.in_fifo_path):
            os.unlink(self.in_fifo_path)
        if os.path.exists(self.out_fifo_path):
            os.unlink(self.out_fifo_path)

        os.mkfifo(self.in_fifo_path)
        os.mkfifo(self.out_fifo_path)

        if not os.path.exists(self.pid_file):
            with open(self.pid_file,"w") as f:
                f.write("%d" % (pid))
            self.in_fifo = open(self.in_fifo_path, "r")

            while os.path.exists(self.pid_file):
                line = self.in_fifo.readline().replace("\n","")
                while line.__len__() == 0 and os.path.exists(self.pid_file):
                    time.sleep(0.1) 
                    line = self.in_fifo.readline().replace("\n", "")
                
                if os.path.exists(self.pid_file):
                    idx = self.analyze(line)
                    out_str = ""
                    print("Analyzing %s" % (line))
                    for item in idx:
                        out_str += item

                    self.out_fifo = open(self.out_fifo_path, "w")
                    self.out_fifo.write(out_str)
                    self.out_fifo.close()

            if not self.in_fifo.closed:
                self.in_fifo.close()
            if not self.out_fifo.closed:
                self.out_fifo.close()
        os.unlink(self.in_fifo_path)
        os.unlink(self.out_fifo_path)

        if os.path.exists(self.pid_file):
            os.unlink(self.pid_file)

d = WordDict()
d.loop_fifo()
