#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013  Vincent Paeder
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

    Custom data validators

"""

import wx
class NumberValidator(wx.PyValidator):
    """
    
        Validator for numbers
    
    """
    def __init__(self,floats=True,negative=True):
        wx.PyValidator.__init__(self)
        self.allowed = [8,9,13,27,48,49,50,51,52,53,54,55,56,57,127,314,316]
        self.floats = floats
        self.negative = negative
        if self.floats:
            self.allowed.append(46)
        if self.negative:
            self.allowed.append(45)
        self.Bind(wx.EVT_CHAR, self.OnChar)
    
    def Clone(self):
        return NumberValidator(floats=self.floats,negative=self.negative)
    
    def OnChar(self, event):
        if self.allowed.count(event.KeyCode)>0:
            event.Skip()
        return
    
    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

class IntegerValidator(NumberValidator):
    """
    
        Validator for integer numbers
    
    """
    def __init__(self):
        NumberValidator.__init__(self,floats=False)
    
    def Clone(self):
        return IntegerValidator()


class PositiveFloatValidator(NumberValidator):
    """
    
        Validator for positive floating point numbers
    
    """
    def __init__(self):
        NumberValidator.__init__(self,floats=True,negative=False)
    
    def Clone(self):
        return PositiveFloatValidator()
