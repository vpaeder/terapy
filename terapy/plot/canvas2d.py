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

    Canvas class for 2D plots

"""

from terapy.plot.base import PlotCanvas
from wx.lib.pubsub import Publisher as pub
from matplotlib.colors import LinearSegmentedColormap
from terapy.plot.plot2d import Plot2D

class PlotCanvas2D(PlotCanvas):
    """
    
        Canvas class for 2D plots

        Properties:
            is_data    -    if True, canvas is meant to display raw measurement data (bool)
            is_filter  -    if True, canvas is meant to display post-processed data (bool)
            dim        -    dimension of plots displayed on this canvas (int)
            name       -    name of canvas type (str)
    
    """
    is_data = True
    name = "2D Plot"
    dim = 2
    def __init__(self, parent=None, id=-1, xlabel="Delay (ps)", ylabel="Distance (um)", xscale="linear", yscale="linear"):
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
        self.dim = 2
        self.set_zoom(False)
        self.set_location(False)
        self.set_selection(False)
        # generate colormap
        cdict = {'red': ((0.0, 0.0, 0.0),(0.5, 1.0, 1.0),(1.0, 1.0, 0.0)),
                'green': ((0.0, 0.0, 0.0),(0.5, 1.0, 1.0),(1.0, 0.0, 0.0)),
                'blue': ((0.0, 0.0, 1.0),(0.5, 1.0, 1.0),(1.0, 0.0, 0.0))}
        self._2d_cmap = LinearSegmentedColormap('my_colormap',cdict,256)        
        cdict = {'red': ((0.0, 0.0, 1.0),(1.0, 1.0, 0.0)),
                'green': ((0.0, 0.0, 1.0),(1.0, 0.0, 0.0)),
                'blue': ((0.0, 0.0, 1.0),(1.0, 0.0, 0.0))}
        self._2d_cmap_pos = LinearSegmentedColormap('my_colormap_pos',cdict,256)
        
        cdict = {'red': ((0.0, 0.0, 0.0),(1.0, 1.0, 0.0)),
                'green': ((0.0, 0.0, 0.0),(1.0, 1.0, 0.0)),
                'blue': ((0.0, 0.0, 1.0),(1.0, 1.0, 0.0))}
        self._2d_cmap_neg = LinearSegmentedColormap('my_colormap_neg',cdict,256)
        # send color change event to notify history from change
        pub.sendMessage("plot.color_change")

    def AddPlot(self,array=None):
        """
        
            Add plot to canvas.
            
            Parameters:
                array    -    data array to be displayed (DataArray)
        
        """
        self.is_full = True
        plt = Plot2D(self,array)
        self.plots.append(plt)
        self.SetPlotColors()
        self.Update()
        return plt
    
    def Update(self, event=None):
        """
        
            Update canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        if len(self.plots)>0:
            # get new instance
            self.get_figure().clear()
            fig = self.get_figure()
            self.axes = fig.gca()
            # plot data
            self.plt = self.axes.imshow(self.plots[0].array.data, origin='lower', cmap=self._2d_cmap, interpolation='nearest')
            # autoscale and generate colorbar
            self.axes.set_aspect('auto')
            self.axes.set_autoscale_on(True)
            self.axes.autoscale_view(True,False,False)
            fig.colorbar(self.plt,format="%0.1e")
            # redraw
            self.draw()
    
    def Delete(self, event=None):
        """
        
            Delete canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        if len(self.plots)>0:
            while len(self.plots)>0:
                plt = self.plots.pop()
                plt.Delete()
            if len(self.plots)==0:
                pub.sendMessage("plot.empty_page", data=self)
    
    def SetName(self, name="Plot"):
        """
        
            Set canvas tab name.
            
            Parameters:
                name    -    name (str)
        
        """
        idx = self.parent.FindCanvas(self)
        if idx>-1:        
            self.parent.SetPageText(idx,name)
    
    def SetImage(self, n=2):
        """
        
            Set canvas tab icon.
            
            Parameters:
                n    -    icon index in parent image list (int)
        
        """
        PlotCanvas.SetImage(self, n)
