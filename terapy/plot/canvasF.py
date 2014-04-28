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

    Canvas class for 1D post-processed data plots

"""

from terapy.plot.canvas1d import PlotCanvas1D
import wx
import functools
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
from terapy.filters import FilterBank
from terapy.core.axedit import AxisInfos, du

class PlotCanvasF(PlotCanvas1D):
    """
    
        Canvas class for 1D post-processed data plots

        Properties:
            is_data    -    False, canvas is not meant to display raw measurement data
            is_filter  -    True, canvas is meant to display post-processed data
            dim=1      -    dimension of plots displayed on this canvas (int)
            name       -    name of canvas type (str)
    
    """
    is_filter = True
    name = "Post-processed data"
    def __init__(self, parent=None, id=-1, xlabel=AxisInfos("Frequency",du["frequency"]), ylabel=AxisInfos("Spectrum",du["voltage"]/du["frequency"]), xscale="linear", yscale="log"):
        """
        
            Initialization.
            Parameters:
                parent    -    parent window (wx.Window)
                id        -    id (int)
                xlabel    -    label and units of abscissa axis ([str,quantities])
                ylabel    -    label and units of ordinate axis ([str,quantities])
                xscale    -    abscissa scale type (linear or log)
                yscale    -    ordinate scale type (linear or log)
        
        """
        PlotCanvas1D.__init__(self,parent,id, xlabel, ylabel, xscale, yscale)
        self.bank = FilterBank()
        pub.subscribe(self.PostProcess, "filter.change")
        self.Bind(wx.EVT_WINDOW_DESTROY,self.OnDelete)
    
    def OnDelete(self, event=None):
        """
        
            Actions triggered when canvas is deleted.
            
            Parameters:
                event    -    wx.Event
        
        """
        PlotCanvas1D.OnDelete(self,event)
        pub.unsubscribe(self.PostProcess, "filter.change")
        event.Skip()

    def OnRightClick(self, event):
        """
        
            Actions triggered on mouse right button click.
            
            Parameters:
                event    -    wx.Event
        
        """
        event.Skip()
        # zoom out on right click
        self.axes.set_autoscale_on(True)
        scl = self.axes.get_yscale()
        if scl=='log':
            self.axes.set_yscale('linear')
        else:
            self.axes.set_yscale('log')
        self.Update()

    def PopupMenuItems(self,menu):
        """
        
            Add popup menu items for canvas to given menu.
            
            Parameters:
                menu    -    wx.Menu
        
        """
        PlotCanvas1D.PopupMenuItems(self, menu)
        
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
        
    def SetFilterBank(self, bank):
        """
        
            Set filter bank associated to canvas.
            
            Parameters:
                bank    -    filter bank (filter.FilterBank)
        
        """
        self.bank = bank
        self.Update()
        
        if self.parent.CurrentPage == self:
            pub.sendMessage("plot.set_filters", inst=self.bank)
            pub.sendMessage("plot.switch_canvas")
        pub.sendMessage("filter.change", inst=self.bank)
    
    def PostProcess(self, inst=None):
        """
        
            Post-process displayed data.
            
            Parameters:
                inst    -    pubsub event data (filter.FilterBank)
        
        """
        if inst == self.bank:
            self.bank.RecomputeReference()
            for x in self.plots:
                x.SetData(self.bank.ApplyFilters(x.source.array))
            self.Update()
            if len(self.children)>0:
                inst = self.children[-1].bank
                self.children[-1].PostProcess(inst)
