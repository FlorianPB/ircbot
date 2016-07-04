#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# IRC Python bot
# Copyright (C) 2016, Art SoftWare
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
# ********************************************************************
# For any questions, feture request or bug reports please contact me
# at support@art-software.fr

from json import loads

quoteBDFile = open("quote.json", "r")
quoteBD = loads(quoteBDFile.read())
quoteBDFile.close()

quoteMashup = open("quotes.txt", "w")
nicknames = list(quoteBD.keys())
nicknames.sort()

for nickname in nicknames:
    quoteMashup.write("  - " + nickname + ":\n")
    for quote in quoteBD[nickname]:
        quoteMashup.write("    « " + quote + " »\n")
    quoteMashup.write("\n")
quoteMashup.close()
