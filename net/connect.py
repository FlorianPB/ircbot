#!/usr/bin/env python3
# -*- coding: utf8 -*-
# vim: foldlevel=1

import socket
import util.log

bot = None

class Connect:
    def __init__(self, botInstance):
        global bot

        self.socket = None
        bot = botInstance

    def start(self):
        """Starts the connection with available info"""
        if self.socket == None:
            bot.log.log("Connecting socket to %s:%d" % (bot.cfg["srv"], bot.cfg["port"]), "net.connect.Connect.start", util.log.INFO)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((bot.cfg["srv"], bot.cfg["port"]))

    def stop(self):
        """Stops the current connection"""
        if self.socket != None:
            bot.log.log("Closing connection", "net.connect.Connect.stop", util.log.INFO)
            self.socket.close()
            self.socket = None

    def sendText(self, text, encoding=""):
        """Sends text to the connection"""
        if self.socket != None:
            if encoding != "":
                self.socket.send(text.encode(encoding))
            else:
                self.socket.send(text.encode())

    def waitText(self, encoding="", bufSize=(2**16)-1):
        """Wait for text from the connection"""
        txt = ""
        if self.socket != None:
            try:
                if encoding != "":
                    txt = self.socket.recv(bufSize).decode(encoding)
                else:
                    txt = self.socket.recv(bufSize).decode()
            except UnicodeDecodeError:
                # I just don't know what went wrong.. But it's okay, I will just ignore it till it goes away ^w^
                txt = ""

        return txt

    def checkText(self, encoding="", bufSize=(2**16)-1):
        """Wait for text from the connection"""
        txt = ""
        if self.socket != None:
            try:
                self.socket.setblocking(False)
                if encoding != "":
                    txt = self.socket.recv(bufSize).decode(encoding)
                else:
                    txt = self.socket.recv(bufSize).decode()
                self.socket.setblocking(True)

            except ( UnicodeDecodeError, BlockingIOError ):
                # UnicodeDecodeError:
                # I just don't know what went wrong.. But it's okay, I will just ignore it till it goes away ^w^
                
                # BlockingIOError:
                # Nothing to poll from the Internet.
                # We'll have to send an empty string ^^

                self.socket.setblocking(True)

        return txt
