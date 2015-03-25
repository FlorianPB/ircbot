#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
import util.log

class Connect:
    def __init__(self, logMethod, srv="chat.freenode.net", port=6667):
        self.srv = srv
        self.port = port
        self.log = logMethod
        self.socket = None

    def start(self):
        """Starts the connection with available info"""
        if self.socket == None:
            self.log("Connecting socket to %s:%d" % (self.srv, self.port), "net.connect.Connect.start", util.log.INFO)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.srv, self.port))

    def stop(self):
        """Stops the current connection"""
        if self.socket != None:
            self.log("Closing connection", "net.connect.Connect.stop", util.log.INFO)
            self.socket.close()
            self.socket = None

    def sendText(self, text, encoding="utf8"):
        """Sends text to the connection"""
        if self.socket != None:
            self.log(text, "net.connect.Connect.sendText", util.log.DEBUG)
            self.socket.send(bytes(text, encoding))

    def waitText(self, encoding="utf8", bufSize=(2**16)-1):
        """Wait for text from the connection"""
        txt = ""
        if self.socket != None:
            txt = str(self.socket.recv(bufSize), encoding)
            self.log(txt, "net.connect.Connect.waitText", util.log.DEBUG)

        return txt
