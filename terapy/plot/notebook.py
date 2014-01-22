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

    Notebook class with canvas handling functions

"""

import wx
from terapy.icons import DataIconList
from terapy.plot import canvas_modules
from terapy.core.dragdrop import HistoryDrop
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
from time import time
import functools

class PlotNotebook(wx.Notebook):
    """
    
        Notebook class with canvas handling functions
    
    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=wx.NotebookNameStr):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                id        -    id (int)
                pos       -    default position
                size      -    default size
                style     -    default style
                name      -    name (str)
        
        """
        wx.Notebook.__init__(self, parent, id, pos, size, style, name)
        self.canvasClock = time()
        self.drag_action = False
        self.drag_tab = -1
        self.drag_target = -1
        self.drag_tab_position = (0,0)
        
        self.imglist = DataIconList()
        self.SetImageList(self.imglist)
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnChangePage, self)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick, self)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick, self)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDblClick, self)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp, self)
        self.Bind(wx.EVT_MOTION, self.OnDrag, self)
        
        self.SetDropTarget(HistoryDrop(self.OnEndDrag))
        pub.subscribe(self.SetDragObject, "history.drag_object")
        pub.subscribe(self.RemoveCanvas, "plot.empty_page")
        pub.subscribe(self.Broadcast, "request_canvas")
        
    def AddCanvas(self, cnv = None, title="Plot"):
        """
        
            Add canvas to notebook.
            
            Parameters:
                cnv    -    canvas (PlotCanvas)
                title  -    name (str)
        
        """
        self.InsertCanvas(cnv, self.GetPageCount(), title)
    
    def OnAddCanvas(self, cls = None, event = None):
        """
        
            Add canvas of given class through menu event (made for popup menu action).
            
            Parameters:
                cls    -    canvas class (PlotCanvas)
                event  -    wx.Event
        
        """
        cnv = cls(self)
        self.AddCanvas(cnv, cnv.name)
        
    def InsertCanvas(self, cnv = None, pos = 0, title="Plot", display=True):
        """
        
            Insert given canvas at given tab position.
            
            Parameters:
                cnv        -    canvas class (PlotCanvas)
                pos        -    position (int)
                title      -    tab name (str)
                display    -    if True, show tab
        
        """
        self.InsertPage(pos, cnv, title, display)
        cnv.SetImage()
    
    def RemoveCanvas(self, inst=None, idx = None):
        """
        
            Remove canvas given by index.
            
            Parameters:
                inst    -    pubsub data
                idx     -    canvas index (int)
        
        """
        if inst!=None:
            idx = self.FindCanvas(inst)
        if idx>-1 and idx<self.PageCount:
            self.DeletePage(idx)
            pub.sendMessage("plot.delete")
            pub.sendMessage("plot.color_change")
    
    def FindCanvas(self, cnv):
        """
        
            Find given canvas index.
            
            Parameters:
                cnv    -    canvas (PlotCanvas)
            
            Output:
                canvas index (int)
        
        """
        for n in range(self.PageCount):
            pg = self.GetPage(n)
            if cnv == pg: return n
        return -1 
    
    def FindPlot(self, plt):
        """
        
            Find given plot and return index of canvas and plot.
            
            Parameters:
                plt    -    plot (Plot)
            
            Output:
                tuple: (canvas index, plot index)
        
        """
        for n in range(self.PageCount):
            cnv = self.GetPage(n)
            pidx = cnv.FindPlot(plt)
            if pidx>-1:
                return (n,pidx)
        return (-1,-1)
    
    def OnRightClick(self, event = None):
        """
        
            Actions triggered on right mouse button click on notebook.
            
            Parameters:
                event    -    wx.Event
        
        """
        (tab,where) = self.HitTest(event.Position)
        if where in (wx.NB_HITTEST_ONLABEL, wx.NB_HITTEST_ONICON, wx.NB_HITTEST_ONITEM, wx.NB_HITTEST_NOWHERE):
            # right click => popup menu
            menu = wx.Menu()
            # build "Add..." sub-menu first
            valid = []
            for x in canvas_modules:
                if x.is_data:
                    valid.append(x)
            if len(valid)>0:
                menuAdd = wx.Menu()
                for x in valid:
                    mitem = menuAdd.Append(wx.NewId(),x.name)
                    self.Bind(wx.EVT_MENU, functools.partial(self.OnAddCanvas,x), id=mitem.Id)
                menu.AppendSubMenu(menuAdd,"Add...")
        if tab>-1:
            pg = self.GetPage(tab)
            # add options if click is on a tab
            mitem = menu.Append(wx.NewId(),"&Rename")
            self.Bind(wx.EVT_MENU, functools.partial(self.RenameTab,tab), id=mitem.Id)
            # add class-specific options
            mitem = menu.Append(wx.NewId(),"&Remove canvas")
            self.Bind(wx.EVT_MENU, pg.Delete, id=mitem.Id)
            pg.PopupMenuItems(menu)
        self.PopupMenu(menu)
    
    def RenameTab(self, idx = -1, event=None):
        """
        
            Actions following a rename request for given tab index.
            
            Parameters:
                idx      -    canvas index (int) 
                event    -    wx.Event
        
        """
        if idx>-1:
            dlg = wx.TextEntryDialog(self,caption="Canvas name", message="Set canvas name:", defaultValue=self.GetPageText(idx))
            if dlg.ShowModal() == wx.ID_OK:
                self.SetPageText(idx, dlg.GetValue())
            dlg.Destroy()
    
    def GetTabStripBoundaries(self):
        """
        
            Compute tab strip boundaries.
            
            Output:
                tuple of int: ((xmin, xmax), (ymin, ymax))
        
        """
        # first, find vertical position of tab
        ms = self.Size
        spos = [0,0]
        spos[0] = spos[0] + min((10,ms[0]))
        # search for min y position
        pos = 0
        ymin = -1
        while pos<ms[1]:
            tab = self.HitTest((spos[0],spos[1]+pos))[0]
            if tab>-1:
                ymin = pos
                break
            pos+=1
        # some tabs have been found
        if ymin>-1:
            # search for max y position
            pos = ms[1]
            while pos>=0:
                tab = self.HitTest((spos[0],spos[1]+pos))[0]
                if tab>-1:
                    ymax = pos
                    break
                pos-=1
            # search for min x position
            pos = 0
            spos[0] = 0
            while pos<ms[0]:
                tab = self.HitTest((spos[0]+pos,spos[1]+(ymax+ymin)/2))[0]
                if tab>-1:
                    xmin = pos
                    break
                pos+=1
            # search for max x position
            pos = ms[0]
            while pos>=0:
                tab = self.HitTest((spos[0]+pos,spos[1]+(ymax+ymin)/2))[0]
                if tab>-1:
                    xmax = pos
                    break
                pos-=1
            return ((xmin, xmax),(ymin,ymax))
        return None
        
    def OnLeftClick(self, event=None):
        """
        
            Actions triggered on left mouse button click on notebook.
            
            Parameters:
                event    -    wx.Event
        
        """
        # test if dragging can occur
        tab = self.HitTest(event.Position)[0]
        if tab>-1:
            self.drag_action = True
            self.drag_tab = self.GetPage(tab)
            self.drag_target = self.GetPage(tab)
        else:
            self.drag_action = False
        event.Skip()

    def OnLeftDblClick(self, event=None):
        """
        
            Actions triggered on right mouse button click on notebook.
            
            Parameters:
                event    -    wx.Event
        
        """
        # test if dragging can occur
        tab = self.HitTest(event.Position)[0]
        if tab>-1:
            self.drag_action = False
            self.RenameTab(tab)
        event.Skip()
    
    def OnDrag(self, event = None):
        """
        
            Actions triggered on drag event.
            
            Parameters:
                event    -    wx.Event
        
        """
        # test on movement if dragging is occurring
        if event.LeftIsDown() and self.drag_action:
            self.MoveTab(event)
        else:
            self.drag_action = False
            event.Skip()
        
    def OnLeftUp(self, event = None):
        """
        
            Actions triggered when left mouse button is released.
            
            Parameters:
                event    -    wx.Event
        
        """
        # reset drag flag
        self.drag_action = False
        event.Skip()
    
    def MoveTab(self, event = None):
        """
        
            Move tab during drag.
            
            Parameters:
                event    -    wx.Event
                
            Indirect parameters:
                self.drag_tab    -    tab to be moved (int)
        
        """
        tab = self.HitTest(event.Position)[0]
        changed = False
        if tab==-1:
            # cursor is not above any tab, locate where it is wrt last recorded tab
            bnd = self.GetTabStripBoundaries()
            if bnd==None: return
            # try 1st if it is in the tab strip area
            if event.Position[1]>=bnd[1][0] and event.Position[1]<=bnd[1][1]:
                # in the tab strip but not on a tab
                if event.Position[0]>=bnd[0][0] and event.Position[0]<=bnd[0][1]:
                    # between two tabs
                    pass
                elif event.Position[0]<bnd[0][0] and event.Position[0]>=0:
                    # before 1st tab
                    self.drag_target = self.GetPage(0)
                    changed = True
                elif event.Position[0]>bnd[0][1] and event.Position[0]<self.Size[0]:
                    # after last tab
                    self.drag_target = None
                    changed = True
        else:
            pg = self.GetPage(tab)
            if pg!=self.drag_target:
                self.drag_target = pg
                changed = True
        
        if changed:
            # move tab
            # check that tab can be move there
            allowed = []
            for n in range(self.PageCount):
                allowed.append(self.GetPage(n))
            allowed.append(None)
            cur = self.CurrentPage
            # if page is a filter plot, can't move
            if cur.source!=None:
                allowed = []
            
            # if page is a source plot, can't move within its own children
            if cur.source==None and len(cur.children)>0:
                child = cur.children[-1]
                allowed.pop(allowed.index(child))
                while len(child.children)>0:
                    child = child.children[-1]
                    allowed.pop(allowed.index(child))
            
            # if plot groups are present, can't move any foreign item into the group
            for n in range(self.PageCount):
                pg = self.GetPage(n)
                if allowed.count(pg)>0:
                    if pg.source!=cur.source and pg.source!=None:
                        allowed.pop(allowed.index(pg))
                    elif pg!=cur.source and pg.source==None and n>0:
                        # also don't allow replacing 1st item of the group
                        allowed.pop(allowed.index(pg))
                    
            
            if allowed.count(self.drag_target)>0 and changed and cur!=self.drag_target:
                # if moved page is a source and has sub-pages, must move everything together
                while cur!=None:
                    idx = self.FindCanvas(cur)
                    # move page
                    sub = self.GetPage(idx)
                    subname = self.GetPageText(idx)
                    subimg = self.GetPageImage(idx)
                    self.RemovePage(idx)
                    if cur.source==None:
                        n = self.FindCanvas(self.drag_target)
                        if n>=self.PageCount or n==-1:
                            self.AddPage(sub,subname,True,subimg)
                        else:
                            self.InsertPage(n,sub,subname,True,subimg)
                    else:
                        n = self.FindCanvas(cur.source)+1
                        if n>=self.PageCount or n==-1:
                            self.AddPage(sub,subname,False,subimg)
                        else:
                            self.InsertPage(n,sub,subname,False,subimg)
                    # find next page to be moved
                    if len(cur.children)>0:
                        cur = cur.children[-1]
                    else:
                        cur = None                
                self.drag_tab = self.drag_target
    
    def Broadcast(self, inst=None):
        """
        
            Send notebook reference through pubsub.
            
            Parameters:
                inst    -    pubsub event data
        
        """
        pub.sendMessage("broadcast_canvas",inst=self)

    def AddPlot(self, target="current", array = None):
        """
        
            Add plot to first available canvas (if none available, add one).
            
            Parameters:
                target    -    if "current", attempt to find existing canvas
                               otherwise, create new canvas
                array     -    data array (DataArray)
        
        """
        # add plot of specified dimension to the adequate canvas, create one if none available
        if array!=None: dim = len(array.shape)
        else: return # no data, can't proceed
        
        if target == "current":
            target = None
            if self.CurrentPage!=None:
                # a plot is currently displayed, check which type
                if self.CurrentPage.dim == dim:
                    if self.CurrentPage.is_data and not(self.CurrentPage.is_full):
                        # this is the right type and accepts new plots, set as target
                        target = self.CurrentPage
                    elif self.CurrentPage.is_filter:
                        # post-processed plot, must find owner
                        target = self.CurrentPage.source
                        while target.source!=None:
                            target = target.source
                        if target.is_full: target=None
                else:
                    # no canvas found yet, search amongst open canvases
                    for n in range(self.PageCount):
                        pg = self.GetPage(n)
                        if pg.dim == dim and pg.is_data and not(pg.is_full):
                            target = pg
                            target.SetVisible()
                            break
        else:
            target = None
        # if no valid target has been found, create one
        if target==None:
            for x in canvas_modules:
                if x.dim==dim and x.is_data:
                    target = x(self)
                    self.AddCanvas(target, target.name)
                    target.SetVisible()
                    break
        
        if target==None:
            print "WARNING: can't add plot of dimension " + str(dim)
            return # no valid target found and cannot create one
        
        # add plot to target
        plt = target.AddPlot(array)
        return plt # return new plot
    
    def OnChangePage(self, event=None):
        """
        
            Actions following page change.
             
            Parameters:
                event    -    wx.Event
        
        """
        event.Skip()
        if self.PageCount==0: return
        page = self.GetPage(event.Selection)
        if page.is_filter:
            pub.sendMessage("plot.set_filters", inst=page.bank)
            pub.sendMessage("plot.enable_filters", inst=True)
        else:
            pub.sendMessage("plot.set_filters", inst=None)
            pub.sendMessage("plot.enable_filters", inst=False)
        pub.sendMessage("plot.switch_canvas")

    def OnEndDrag(self, x, y, data):
        """
        
            Actions consecutive to drop on plot notebook.
            
            Parameters:
                x,y    -    coordinates of drop action (int)
                data   -    dropped data (str)
                            Passing drag and drop data in wxpython is incovenient.
                            Alternative used here: data is stored as self.drag_object
        
        """
        if self.drag_object!=None:
            pg = self.GetCurrentPage()
            # check that current page can receive dropped data
            if len(self.drag_object.shape)==pg.dim:
                # if the dimension is ok, the type of canvas must be checked
                if pg.is_data:
                    target = pg
                elif pg.is_filter:
                    target = pg
                    while not(target.is_data):
                        target = target.source
                if self.drag_object.plot==None:
                    # dropped data isn't plotted anywhere => add to target
                    self.drag_object.plot = target.AddPlot(self.drag_object)
                else:
                    # already plotted => delete and replot
                    self.drag_object.plot.Delete()
                    self.drag_object.plot = target.AddPlot(self.drag_object)
                target.SetPlotColors()
    
    def SetDragObject(self, inst):
        """
        
            Set drag object from pubsub event (used in drag and drop actions).
            
            Parameters:
                inst    -    pubsub event data
        
        """
        self.drag_object = inst
        