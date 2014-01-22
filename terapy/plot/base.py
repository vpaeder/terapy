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

    Base classes for canvases and plots

"""

import wx
from terapy.core.axedit import ConvertUnits, FormatUnits
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub

class PlotCanvas(wx.Panel):
    """
    
        Generic canvas class.
        
        Properties:
            is_data    -    if True, canvas is meant to display raw measurement data (bool)
            is_filter  -    if True, canvas is meant to display post-processed data (bool)
            dim        -    dimension of plots displayed on this canvas (int)
            name       -    name of canvas type (str)
    
    """
    is_data = False
    is_filter = False
    dim = -1
    name = "Plot"
    def __init__(self, parent=None, id=-1,  *args, **kwargs):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                id        -    id (int)
                
        """
        if not(isinstance(self,wx.Panel)):
            wx.Panel.__init__(self,parent,id)
        self.parent = parent
        self.plots = [] # plots on this canvas
        self.is_full = False # if True, tells that canvas can't receive more plots 
        self.children = [] # canvases linked to this one (e.g. post-processing canvases)
        self.source = None # master canvas
        self.drag_object = None
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDelete, self)
        pub.subscribe(self.ChangeDefaultUnits, "default_units.changed")
        
    
    def EditAxes(self, event=None):
        """
        
            Open dialog to change axes labels and units.
            
            Parameters:
                event    -    wx.Event
        
        """
        from terapy.core.axedit import AxesPropertiesDialog
        old_labels = [x.copy() for x in self.labels]
        dlg = AxesPropertiesDialog(self,axlist=old_labels)
        if dlg.ShowModal() == wx.ID_OK:
            labels = dlg.GetValue()
            dlg.Destroy()
            ConvertUnits(self.labels, labels)
            for x in self.plots:
                x.array.Rescale(new_labels=self.labels, defaults=old_labels)
                x.SetData(x.array)
            
            wx.CallAfter(self.Update)
        else:
            dlg.Destroy()
    
    def ChangeDefaultUnits(self, inst=None):
        """
        
            Change canvas units and scale plots to default units.
            
            Parameters:
                inst    -    pubsub data (not used)
        
        """
        # convert plot units to new units
        units = [FormatUnits(x.units) for x in self.labels]
        for x in units:x._magnitude=1.0
        
        # create new labels
        labels = [x.copy() for x in self.labels]
        for n in range(len(labels)):
            labels[n].units = units[n]
        
        # convert plot data to new units
        for x in self.plots:
            x.array.Rescale(labels,self.labels)
            x.SetData(x.array)
        
        # set new labels
        self.labels = labels
        
        # update
        wx.CallAfter(self.Update)
    
    def OnDelete(self, event=None):
        """
        
            Clean up before destroying object.
            
            Parameters:
                event    -    wx.Event
        
        """
        pub.unsubscribe(self.ChangeDefaultUnits, "default_units.changed")
        event.Skip()
    
    def Update(self, event=None):
        """
        
            Update canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        pass
    
    def PopupMenuItems(self,menu):
        """
        
            Add popup menu items for canvas to given menu.
            
            Parameters:
                menu    -    wx.Menu
        
        """
        pass
    
    def AddCanvas(self, cls, event):
        """
        
            Add canvas of given class type to parent.
            Helper function to respond to popup menu action.
            
            Parameters:
                cls    -    canvas class
                event  -    wx.Event
        
        """
        cnv = cls(self.parent)
        self.parent.AddCanvas(cnv,cls.name)
    
    def ClearCanvas(self, event=None):
        """
        
            Actions required to clear canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        while len(self.plots)>0:
            self.plots[0].Delete()
    
    def SetName(self, name="Plot"):
        """
        
            Set canvas name.
            
            Parameters:
                name    -    name (str)
        
        """
        pass # general case: plot name and canvas page name are independent
    
    def SetVisible(self):
        """
        
            Show canvas.
        
        """
        idx = self.parent.FindCanvas(self)
        if idx>-1:
            self.parent.ChangeSelection(idx)
    
    def SetImage(self, n=-1):
        """
        
            Set canvas tab icon.
            
            Parameters:
                n    -    icon index in parent image list (int)
        
        """
        idx = self.parent.FindCanvas(self)
        if idx>-1 and n>-1:
            self.parent.SetPageImage(idx,n)
    
    def AddPlot(self,array=None):
        """
        
            Add plot to canvas.
            
            Parameters:
                array    -    data array to be displayed (DataArray)
        
        """
        return None
    
    def RemovePlot(self, plt):
        """
        
            Remove given plot from plot list.
            
            Parameters:
                plt    -    plot (Plot)
        
        """
        if self.plots.count(plt)>0:
            self.plots.pop(self.plots.index(plt)).Delete()
    
    def FindPlot(self, plt):
        """
        
            Find plot index in canvas.
            
            Parameters:
                plt    -    plot to be found (Plot)
            
            Output:
                plot index (int)
        
        """
        if self.plots.count(plt)>0:
            return self.plots.index(plt)
        else:
            return -1

    def SetPlotColors(self):
        """
        
            Set canvas plot colors.
        
        """
        pass
    
class Plot():
    """
    
        Generic plot class.
    
    """
    def __init__(self, canvas=None, array=None):
        """
        
            Initialization.
            
            Parameters:
                canvas    -    parent canvas (PlotCanvas)
                array     -    plotted data array (DataArray)
        
        """
        self.canvas = canvas
        self.array = array
        self.color = wx.Colour(0,0,0)
        self.plot = None
        self.children = [] # plots associated to this one (e.g. post-processed plots)
        self.source = None # master plot
    
    def SetData(self, data):
        """
        
            Set plot data.
            
            Parameters:
                data     -    data array (DataArray)
        
        """
        pass
    
    def GetData(self, data):
        """
        
            Get plot data.
            
            Output:
                data array (DataArray)
        
        """
        return None
    
    def SetColor(self, col):
        """
        
            Set plot color.
            
            Parameters:
                col    -    color (wx.Color)
        
        """
        if isinstance(col,wx.Colour):
            self.color = col
        elif isinstance(col,tuple):
            self.color = wx.Colour(int(col[0]*255),int(col[1]*255),int(col[2]*255))
        #if self.array!=None: self.array.color = col
    
    def GetColor(self):
        """
        
            Get plot color.
            
            Output:
                color (wx.Color)
        
        """
        return self.color
    
    def Update(self):
        """
        
            Update plot display.
        
        """
        self.canvas.Update()
    
    def Recompute(self):
        """
        
            Recompute plot data.
        
        """
        if self.canvas.is_filter:
            array = self.source.GetData()
            self.SetData(self.canvas.bank.ApplyFilters(array))
        if len(self.children)>0:
            self.children[0].Recompute()
        self.Update()
    
    def Delete(self):
        """
        
            Delete plot.
        
        """
        pass

    def SetPlotColors(self):
        """
        
            Wrapper to parent canvas SetPlotColors function.
        
        """
        self.canvas.SetPlotColors()
