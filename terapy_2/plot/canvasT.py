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

    Canvas class for 1D raw data plots

"""

from terapy.plot.canvas1d import PlotCanvas1D
import wx
from wx.lib.pubsub import Publisher as pub
import functools
import wxmpl
from terapy.core.axedit import AxisInfos, du

class PlotCanvasT(PlotCanvas1D):
    """
    
        Canvas class for 1D raw data plots

        Properties:
            is_data    -    True, canvas is meant to display raw measurement data
            is_filter  -    False, canvas is not meant to display post-processed data
            dim=1      -    dimension of plots displayed on this canvas (int)
            name       -    name of canvas type (str)
    
    """
    is_data = True
    name = "Time domain data"
    def __init__(self, parent=None, id=-1, xlabel=AxisInfos("Delay",du["time"]), ylabel=AxisInfos("Signal",du["voltage"]), xscale="linear", yscale="linear"):
        PlotCanvas1D.__init__(self,parent,id, xlabel, ylabel, xscale, yscale)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDblClick)
        
    def OnLeftDblClick(self, event):
        """
        
            Actions triggered after double-click on left mouse button on canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        event.StopPropagation()
        # this implements the goto-cursor-position functionality of the scan stage
        x, y = event.GetPositionTuple() 
        wh = self.GetSize()
        axes = wxmpl.find_axes(self, x, wh[1] - y)    # mirror y coordinates to get proper orientation
        # send position further
        pub.sendMessage("plot.move_axis", data=axes[1]) 

    def PopupMenuItems(self,menu):
        """
        
            Add popup menu items for canvas to given menu.
            
            Parameters:
                menu    -    wx.Menu
        
        """
        PlotCanvas1D.PopupMenuItems(self, menu)
        mitem = menu.Append(wx.NewId(),"&Clear canvas")
        menu.Bind(wx.EVT_MENU, self.ClearCanvas, id=mitem.Id)
        
        # Edit axes
        mitem = menu.Append(wx.NewId(),"&Edit axes")
        menu.Bind(wx.EVT_MENU, self.EditAxes, id=mitem.Id)
        
        # post-processing banks
        menuAdd = wx.Menu()
        from terapy.filters import GetFilterFiles
        fl = GetFilterFiles()
        mitem = menuAdd.Append(wx.NewId(),"Default filter bank")
        self.parent.Bind(wx.EVT_MENU, functools.partial(self.AddFilterCanvas,""), id=mitem.Id)
        for x in fl:
            mitem = menuAdd.Append(wx.NewId(),x[1])
            self.parent.Bind(wx.EVT_MENU, functools.partial(self.AddFilterCanvas,x[0]), id=mitem.Id)
        menu.AppendSubMenu(menuAdd,"&Add post-processing canvas")
        
        if len(self.children)>0:
            mitem = menu.Append(wx.NewId(),"&Remove post-processing canvases")
            self.parent.Bind(wx.EVT_MENU, self.RemoveFilterCanvases, id=mitem.Id)
