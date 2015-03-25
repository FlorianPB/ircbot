#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket

class Connect:
    def __init__(self, srv="chat.freenode.net", port=6667):
        self.srv = srv
        self.port = port
        self.channel = channel
        self.socket = None

    def start(self):
        """Starts the connection with available info"""
        if self.socket == None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.srv, self.port))

    def stop(self):
        """Stops the current connection"""
        if self.socket != None:
            self.socket.close()
            self.socket = None

    def sendText(self, text, encoding="utf8"):
        """Sends text to the connection"""
        if self.socket != None:
            self.socket.send(bytes(text, encoding))

    def waitText(self, encoding="utf8", bufSize=(2**16)-1):
        """Wait for text from the connection"""
        txt = ""
        if self.socket != None:
            txt = str(self.socket.recv(bufSize), encoding)

        return txt
