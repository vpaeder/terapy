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

    Custom tooltip widget

"""

from wx.lib.agw.supertooltip import SuperToolTip
import wx

class ToolTip(SuperToolTip):
    """
    
        Attempt to handle lousy word wrapping occurring with Windows.
        SuperToolTip handles word wrap well, but other issues arise (i.e. lousy timing of show/hide vs mouse events)
    
    """
    def __init__(self,message="",header="",target=None):
        """
        
            Initialization.
            
            Parameters:
                message    -    tool tip message (str)
                header     -    tool tip header (str)
                target     -    tool tip target control (wx.Window)
         
        """
        SuperToolTip.__init__(self,message=message, header=header)
        if wx.Platform == '__WXMSW__' and False:
            # with Windows, native tooltip wraps words => use custom tooltip instead
            # super tooltip looks good but has a very annoying behaviour
            self.SetTarget(target)
            self.SetDrawHeaderLine(True)
            self.SetTopGradientColour(wx.WHITE)
            self.SetMiddleGradientColour(wx.WHITE)
            self.SetBottomGradientColour(wx.WHITE)
            self.SetMessageFont(wx.Font(9,wx.FONTFAMILY_TELETYPE,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL))
            self.SetStartDelay(2)
            self.SetEndDelay(5)
        else:
            # with GTK, use native tooltip
            message = message.split('\n')
            caption = []
            text = []
            for x in message:
                x = x.split('->')
                caption.append(x[0].strip())
                text.append(x[1].strip())
            ml = max(map(len,caption))
            caption = map(lambda x:x.ljust(ml),caption)
            if wx.Platform == '__WXMSW__':
                message = "\n".join(map(lambda x:x[0]+"  ->  " + x[1],zip(caption,text)))
            else:
                message = "\n".join(map(lambda x:x[0]+"\t->\t" + x[1],zip(caption,text)))
            target.SetToolTipString(message)
