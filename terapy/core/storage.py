#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Vincent Paeder
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

   Simple storage class 

"""

class Storage():
    def __init__(self):
        self._taglist = []

    def Save(self, data, tag):
        if tag!="_taglist":
            if not(hasattr(self,tag)):
                self._taglist.append(tag)
            setattr(self,tag,data)

    def Read(self, tag):
        if hasattr(self,tag) and tag!="_taglist":
            return getattr(self,tag)
        else:
            return None
    
    def Remove(self, tag):
        if hasattr(self,tag) and tag!="_taglist":
            delattr(self, tag)
            self._taglist.pop(self._taglist.index(tag))
        
    def GetTags(self):
        return self._taglist
