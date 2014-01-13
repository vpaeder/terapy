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

    Multiply by factor

"""

from terapy.filters.base import Filter
import wx
from terapy.core import icon_path

class Multiply(Filter):
    """
    
        Multiply by factor
    
    """
    __extname__ = "Multiply by factor"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.factor = 1.0
        self.config = ["factor"]

    def apply_filter(self, array):
        array.data = array.data*self.factor
        return True
    
    def set_filter(self, parent = None):
        dlg = wx.TextEntryDialog(parent,message="Multiplication factor",defaultValue=str(self.factor))
        if dlg.ShowModal() == wx.ID_OK:
            self.factor = float(dlg.GetValue())
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_icon(self):
        return wx.Image(icon_path + "filter-multiply.png").ConvertToBitmap()
