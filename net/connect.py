#!/usr/bin/env python3
# -*- coding: utf8 -*-

import socket
import util.log

class Connect:
    def __init__(self, logMethod, srv="chat.freenode.net", port=6667):
        """logMethod must be a util.log.Log.log method bound to a util.log.Log object (to avoid the need to specify filename, etc)"""
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
            if encoding != "":
                txt = self.socket.recv(bufSize).decode(encoding)
            else:
                txt = self.socket.recv(bufSize).decode()

        return txt
