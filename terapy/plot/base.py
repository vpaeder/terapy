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
import wxmpl
from wx.lib.pubsub import Publisher as pub
from terapy.core.dragdrop import HistoryDrop

class PlotCanvas(wxmpl.PlotPanel):
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
    def __init__(self, parent=None, id=-1, xlabel="Delay (ps)", ylabel="Signal (V)", xscale="linear", yscale="linear"):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                id        -    id (int)
                xlabel    -    label of abscissa axis (str)
                ylabel    -    label of ordinate axis (str)
                xscale    -    abscissa scale type (linear or log)
                yscale    -    ordinate scale type (linear or log)
        
        """
        wxmpl.PlotPanel.__init__(self,parent,id)
        self.parent = parent
        self.plots = [] # plots on this canvas
        self.is_full = False # if True, tells that canvas can't receive more plots 
        self.children = [] # canvases linked to this one (e.g. post-processing canvases)
        self.source = None # master canvas
        self.drag_object = None
        
        fig = self.get_figure()
        self.axes = fig.gca()
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.grid(True)
        self.axes.set_autoscale_on(True)
        self.axes.set_xscale(xscale)
        self.axes.set_yscale(yscale)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick, self)
        self.SetDropTarget(HistoryDrop(self.OnEndDrag))
        
        pub.subscribe(self.SetDragObject, "history.drag_object")
        self.Bind(wx.EVT_WINDOW_DESTROY,self.OnDelete)
        
    def Update(self, event=None):
        """
        
            Update canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        pass
    
    def OnDelete(self, event=None):
        """
        
            Actions triggered when canvas is deleted.
            
            Parameters:
                event    -    wx.Event
        
        """
        pub.unsubscribe(self.SetDragObject, "history.drag_object")
        wxmpl.PlotPanel.OnDestroy(self, event)
    
    def OnRightClick(self, event):
        """
        
            Actions triggered on mouse right button click.
            
            Parameters:
                event    -    wx.Event
        
        """
        # zoom out on right click
        event.Skip()
        self.axes.set_autoscale_on(True)
        self.Update()
    
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
    
    def OnEndDrag(self, x, y, data):
        """
        
            Actions consecutive to drop on canvas.
            
            Parameters:
                x,y    -    coordinates of drop action (int)
                data   -    dropped data (str)
                            Passing drag and drop data in wxpython is incovenient.
                            Alternative used here: data is stored as self.drag_object
        
        """
        if self.drag_object!=None:
            if len(self.drag_object.shape)==self.dim:
                if self.is_data:
                    target = self
                elif self.is_filter:
                    target = self
                    while not(target.is_data):
                        target = target.source
                if self.drag_object.plot==None:
                    self.drag_object.plot = target.AddPlot(self.drag_object)
                else:
                    self.drag_object.plot.Delete()
                    self.drag_object.plot = target.AddPlot(self.drag_object)
                self.SetPlotColors()
    
    def SetDragObject(self, inst):
        """
        
            Set drag object from pubsub event (used in drag and drop actions).
            
            Parameters:
                inst    -    pubsub event data
        
        """
        self.drag_object = inst.data

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
        self.color = wx.Color(0,0,0)
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
        if isinstance(col,wx.Color):
            self.color = col
        elif isinstance(col,tuple):
            self.color = wx.Color(int(col[0]*255),int(col[1]*255),int(col[2]*255))
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
