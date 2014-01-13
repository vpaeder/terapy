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

    Canvas class for 1D plots

"""

from terapy.plot.base import PlotCanvas
from terapy.plot.plot1d import Plot1D
from wx.lib.pubsub import Publisher as pub
from terapy.filters import FilterBank

class PlotCanvas1D(PlotCanvas):
    """
    
        Canvas class for 1D plots

        Properties:
            is_data    -    if True, canvas is meant to display raw measurement data (bool)
            is_filter  -    if True, canvas is meant to display post-processed data (bool)
            dim        -    dimension of plots displayed on this canvas (int)
            name       -    name of canvas type (str)
    
    """
    name = "1D Plot"
    dim = 1
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
        PlotCanvas.__init__(self,parent,id, xlabel, ylabel, xscale, yscale)
        self.fcanvas = []
        
    def Update(self, event=None):
        """
        
            Update canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.axes.relim()
        try:
            # this can fail with invalid data (e.g. negative values with log scale)
            self.axes.autoscale_view()
        except:
            pass
        self.draw()
        
    def SetImage(self, n=1):
        """
        
            Set canvas tab icon.
            
            Parameters:
                n    -    icon index in parent image list (int)
        
        """
        PlotCanvas.SetImage(self, n)

    def AddPlot(self,array=None):
        """
        
            Add plot to canvas.
            
            Parameters:
                array    -    data array to be displayed (DataArray)
        
        """
        if self.is_filter:
            plt = Plot1D(self,self.bank.ApplyFilters(array))
        elif self.is_data:
            plt = Plot1D(self,array)
        self.plots.append(plt)
        for x in self.children:
            nplt = x.AddPlot(plt.GetData())
            nplt.source = plt
            plt.children.append(nplt)
        self.SetPlotColors()
        self.Update()
        return plt
    
    def RemovePlot(self, pos):
        """
        
            Remove given plot from canvas.
            
            Parameters:
                pos    -    plot index (int)
        
        """
        self.plots.pop(pos)
        self.SetPlotColors()
        self.Update()

    def Delete(self, event=None):
        """
        
            Delete canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.ClearCanvas()
        for x in self.children:
            x.Delete()
            x.children = []
        if self.source!=None:
            self.source.children.pop(self.source.children.index(self))
        pub.sendMessage("plot.empty_page", data=self)
    
    def SetPlotColors(self):
        """
        
            Set canvas plot colors.
        
        """
        # get number of arrays with custom color
        Nc = 0
        for x in self.plots:
            x.color = None
            if x.array!=None:
                if x.array.color!=None:
                    x.color = x.array.color
                    Nc+=1

        Np = len(self.plots)-Nc        
        np = Np-1
        for x in self.plots:
            if x.color != None:
                color = x.color
            else:
                color = (1.0-(np+1.0)/(Np*1.0),0.0,(np+1.0)/(Np*1.0))
                np -= 1
            if x.source==None:
                x.SetColor(color)
                y = x.children
                while len(y)>0:
                    for z in y:
                        z.SetColor(color)
                    y = y[-1].children
        
        # send color change event to notify history from change
        pub.sendMessage("plot.color_change")
    
    def AddFilterCanvas(self, fname = "", event=None):
        """
        
            Add post-processing canvas linked to current canvas.
            
            Parameters:
                fname    -    file name of post-processing filter bank (str, if none or invalid, load default bank)
                event    -    wx.Event
        
        """
        # add post-processing canvas if any adapted type available
        from terapy import plot
        for x in plot.canvas_modules:
            if x.dim == self.dim and x.is_filter:
                # found one, add suitable canvas
                cnv = x(self.parent)
                # must find where
                pos = self.parent.FindCanvas(self) + 1
                z = self
                while len(z.children)>0:
                    z = z.children[-1]
                    pos += 1
                self.parent.InsertCanvas(cnv, pos, self.name + " (filtered)")
                z.children.append(cnv)
                # if canvas has a parent canvas, add suitable reference to new canvas
                cnv.source = self if z.source==None else z
                # if current canvas contains plots, add processed copies to new canvas
                for y in self.plots:
                    arr = y.GetData()
                    plt = y.__class__(cnv,arr)
                    plt.SetColor(y.GetColor())
                    cnv.plots.append(plt)
                    # if canvas has a parent canvas, add suitable references to new plot
                    # otherwise, set current plot as source to new plot
                    z = y
                    while len(z.children)>0:
                        z = z.children[-1]
                    z.children.append(plt)
                    plt.source = y if y.source==None else z
                # set filter bank
                bank = FilterBank(dim=self.dim)
                if fname=="":
                    bank.DefaultFilters()
                else:
                    bank.LoadFilterList(fname)
                if cnv.source!=None:
                    if cnv.source.is_filter:
                        bank.parent = cnv.source.bank
                        bank.parent.children.append(bank)
                cnv.SetFilterBank(bank)
                break
    
    def RemoveFilterCanvases(self, event=None):
        """
        
            Remove post-processing canvases associated with this canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        # first remove cross-references between associated filter banks
        if self.is_filter:
            for x in self.bank.children:
                x.parent = None
            self.bank.children = []
        # then delete the canvas objects
        for x in self.children:
            x.RemoveFilterCanvases()
            x.Delete()
        self.children = []
