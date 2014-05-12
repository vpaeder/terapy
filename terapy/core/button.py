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

    Run/Stop button

"""

import wx
import platform
from terapy.core import icon_path

class RunButton(wx.BitmapButton):
    """
    
        Graphical run/stop button with toggle function
      
    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.BU_AUTODRAW, validator=wx.DefaultValidator, name=wx.ButtonNameStr):
        """
        
            Initialization.
        
        """
        if wx.Platform == '__WXMSW__' and platform.win32_ver()[0]=='XP' and wx.VERSION[0]<3:
            self.image = [wx.Image(icon_path + "scan-stop-win.png"),wx.Image(icon_path + "scan-start-win.png")]
        else:
            self.image = [wx.Image(icon_path + "scan-stop.png"),wx.Image(icon_path + "scan-start.png")]
        map(lambda x: x.ConvertAlphaToMask(128),self.image)
        self.image = map(lambda x: x.ConvertToBitmap(), self.image)
        if wx.VERSION[0]==3:
            self.color = [wx.Colour(255,0,0), wx.Colour(0,255,0)]
        else:
            self.color = [wx.Color(255,0,0), wx.Color(0,255,0)]
        self.state = True
        wx.BitmapButton.__init__(self, parent, id, self.image[self.state], pos, size, style, validator, name)
        self.SetBackgroundColour(self.color[self.state])
    
    def Switch(self, state=True):
        """
        
            Switch between run and stop states (run = True, stop = False)
            
            Parameters:
                state    -    state (bool, run = True, stop = False)
        
        """
        self.state = state
        self.SetBitmapLabel(self.image[self.state])
        self.SetBackgroundColour(self.color[self.state])

class OnOffIndicator(wx.Panel):
    """
    
        Graphical boolean indicator
      
    """
    def __init__(self, parent, label="text"):
        """
        
            Initialization.
        
        """
        wx.Panel.__init__(self,parent)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.image = [wx.Image(icon_path + "toggle-off.png"),wx.Image(icon_path + "toggle-on.png")]
        map(lambda x: x.ConvertAlphaToMask(128),self.image)
        self.image = map(lambda x: x.ConvertToBitmap(), self.image)
        self.state = True
        self.indicator = wx.BitmapButton(self,style=wx.NO_BORDER, bitmap=self.image[self.state])
        self.text = wx.StaticText(self,-1,label)
        hbox.Add(self.indicator,0,wx.EXPAND|wx.ALL,2)
        hbox.Add(self.text,0,wx.EXPAND|wx.ALL,2)
        self.SetSizerAndFit(hbox)
            
    def Switch(self, state=True):
        """
        
            Switch between on and off states
            
            Parameters:
                state    -    state (bool)
        
        """
        self.state = state
        self.indicator.SetBitmapLabel(self.image[self.state])
    
    def SetLabel(self, text=""):
        self.text.SetLabel(text)
