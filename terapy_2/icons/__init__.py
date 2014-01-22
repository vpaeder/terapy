#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2014  Vincent Paeder
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

    Functions and classes to handle icons.
    
    Some of the icons contained in this folder are taken from the Tango Desktop Project
    http://tango.freedesktop.org

"""

import wx
from terapy.core import icon_path

class DataIconList(wx.ImageList):
    """
    
        Data icon list class
        
        Image list with pre-loaded data type icons
    
    """
    def __init__(self):
        wx.ImageList.__init__(self, 16,16)
        self.Add(wx.Image(icon_path + "icon_0D.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        self.Add(wx.Image(icon_path + "icon_1D.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        self.Add(wx.Image(icon_path + "icon_2D.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        self.Add(wx.Image(icon_path + "icon_3D.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        self.Add(wx.Image(icon_path + "icon_1Dr.png",wx.BITMAP_TYPE_PNG).ConvertToBitmap())
