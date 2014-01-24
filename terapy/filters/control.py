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

    Filter bank control widget

"""

import numpy as np
from pylab import Line2D
import os
import wx
from terapy.core.dataman import DataArray
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin 
from terapy.core import icon_path
from terapy.core.plotpanel import PlotPanel
from terapy.core.dragdrop import FilterDrop, FilterDragObject
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
from terapy.filters import GetModules, FilterBank
import functools

class FilterList(wx.ListCtrl,ListCtrlAutoWidthMixin):
    """
    
        Listbox with auto width mixin
    
    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr):
        wx.ListCtrl.__init__(self, parent, id=id, pos=pos, size=size, style=style, validator=validator, name=name)
        ListCtrlAutoWidthMixin.__init__(self) # add auto width support
        self.setResizeColumn(0)

class FilterControl(wx.Panel):
    """
    
        Filter bank control widget
    
    """
    def __init__(self, parent = None, dim = 1):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                dim       -    dimension (int)
        
        """
        wx.Panel.__init__(self, parent)
        self.bank = FilterBank()
        self.dim = dim
        
        # filter list
        self.list = FilterList(self, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER)
        self.list.SetMaxSize((200,-1))
        
        self.list.InsertColumn(0,"Name")
        self.img_list = wx.ImageList(16,16)
        from terapy.core.tooltip import ToolTip
        ToolTip("Double click  ->  Change properties\nRight click   ->  Menu\nShift+Left    ->  Enable/disable","Usage",self.list)
        
        modules = GetModules(self.dim)
        for x in modules:
            self.img_list.Add(x().get_icon())
        
        self.list.SetImageList(self.img_list,wx.IMAGE_LIST_SMALL)
        
        # window preview
        self.label_plot = wx.StaticText(self, -1, "Apodization window")
        self.plot_filter = PlotPanel(self, -1)
        self.plot_filter.SetMaxSize((150,100))
        self.plot_filter.SetMinSize((150,100))

        # further controls
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.list, 1, wx.EXPAND|wx.TOP, 2)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.button_up = wx.BitmapButton(self, -1, wx.Image(icon_path + "go-up.png").ConvertToBitmap())
        self.button_down = wx.BitmapButton(self, -1, wx.Image(icon_path + "go-down.png").ConvertToBitmap())
        self.button_add = wx.BitmapButton(self, -1, wx.Image(icon_path + "list-add.png").ConvertToBitmap())
        self.button_remove = wx.BitmapButton(self, -1, wx.Image(icon_path + "list-remove.png").ConvertToBitmap())
        hbox.Add(self.button_up, 0, wx.EXPAND|wx.ALL, 2)
        hbox.Add(self.button_down, 0, wx.EXPAND|wx.ALL, 2)
        hbox.Add(self.button_add, 0, wx.EXPAND|wx.ALL, 2)
        hbox.Add(self.button_remove, 0, wx.EXPAND|wx.ALL, 2)
        self.sizer.Add(hbox, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 2)
        self.sizer.Add(self.label_plot, 0, wx.EXPAND|wx.TOP, 2)
        self.sizer.Add(self.plot_filter, 0, wx.EXPAND|wx.TOP|wx.CENTER, 2)
        
        # bindings
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnFilterListRightClick, self.list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnFilterDoubleClick, self.list)
        self.list.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnStartDrag, self.list)
        self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnFilterListRightClick)
        self.list.Bind(wx.EVT_LEFT_DOWN, self.OnFilterLeftClick)
        self.Bind(wx.EVT_BUTTON, lambda x:self.OnMove(-1), self.button_up)
        self.Bind(wx.EVT_BUTTON, lambda x:self.OnMove(+1), self.button_down)
        self.Bind(wx.EVT_BUTTON, self.OnFilterListRightClick, self.button_add)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveFilter, self.button_remove)
        
        # pubsub bindings
        pub.subscribe(self.SetReference, "history.set_reference")
        pub.subscribe(self.SetFilterBank, "plot.set_filters")
        pub.subscribe(self.EnableControl, "plot.enable_filters")
        pub.subscribe(self.OnFilterUpdate, "plot.apply_filters")
        pub.subscribe(self.UpdateFilterDisplay, "plot.switch_canvas")
        pub.subscribe(self.RefreshFilters, "filter.change")
        
        # drag and drop enable
        self.list.SetDropTarget(FilterDrop(self.OnEndDrag))
        
        # filter preview
        figFi = self.plot_filter.get_figure()
        axeFi =  figFi.gca()
        axeFi.get_xaxis().set_visible(False)
        axeFi.get_yaxis().set_visible(False)
        self.plot_filter.set_zoom(False)
        self.plot_filter.set_selection(False)
        self.plot_filter.set_location(False)
        self.plot_filter.set_cursor(False)
        self.plot_filter.set_crosshairs(False)
        self.line_filter = Line2D([-1.5,-1,-1,1,1,1.5],[0,0,1,1,0,0])
        axeFi.add_line(self.line_filter)
        axeFi.add_line(Line2D([-1,-1],[-1,2],ls='--',color='k'))
        axeFi.add_line(Line2D([1,1],[-1,2],ls='--',color='k'))
        self.line_filter.set_visible(True)
        axeFi.set_xlim(-1.5,1.5)
        axeFi.set_ylim(-0.5,1.5)
        self.plot_filter.draw()
        
        # display fitting stuff 
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.sizer.SetSizeHints(self)
        
    def RefreshFilters(self, inst=None):
        """
        
            Refresh displayed filter list.
            
            Parameters:
                inst    -    pubsub event data (FilterBank)
        
        """
        if inst!=None:
            if inst!=self.bank: return
        # store currently selected items
        sels = []
        itm = self.list.GetFirstSelected()
        while itm>-1:
            sels.append(itm)
            itm = self.list.GetNextSelected(itm)
        # rebuild filter list
        modules = GetModules(self.dim)
        self.list.DeleteAllItems()
        if not(isinstance(self.bank,FilterBank)): return
        for ft in self.bank.filters:
            if modules.count(ft.__class__)>0:
                n = modules.index(ft.__class__)
                self.list.InsertImageStringItem(self.list.GetItemCount(),ft.name,n)
                f = self.list.GetItemFont(self.list.GetItemCount()-1)
                f.SetPointSize(10)
                if ft.is_active:
                    f.SetStyle(wx.FONTSTYLE_NORMAL)
                else:
                    f.SetStyle(wx.FONTSTYLE_ITALIC)
                self.list.SetItemFont(self.list.GetItemCount()-1,f)
        # select previously selected items
        for x in sels:
            self.list.Select(x, True)
    
    def SetFilterBank(self, inst):
        """
        
            Set filter bank through pubsub.
            
            Parameters:
                inst    -    pubsub event data (FilterBank)
        
        """
        self.bank = inst
        self.RefreshFilters()
    
    def EnableControl(self, inst):
        """
        
            Set control to given state (through pubsub)
            
            Parameters:
                inst    -    pubsub event data (bool)
        
        """
        self.Enable(inst)
    
    def LoadFilterList(self, event=None, fname=""):
        """
        
            Load filter bank from given file or open dialog box.
            Set result to displayed filter bank.
            
            Parameters:
                event    -    wx.Event
                fname    -    file name (str, open dialog box if empty)
        
        """
        if fname=="":
            dlg = wx.FileDialog(self, "Choose input file", os.getcwd(),"", "Configuration file (*.ini)|*.ini|All files (*.*)|*.*", wx.OPEN)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            fname = dlg.GetPath()
            dlg.Destroy()
        
        self.bank.LoadFilterList(fname)
        self.RefreshFilters()
        self.OnFilterUpdate()
        
    def SaveFilterList(self, event=None, fname=""):
        """
        
            Save current filter list to given file.
            
            Parameters:
                event    -    wx.Event
                fname    -    file name (str)
        
        """
        if fname=="":
            dlg = wx.FileDialog(self, "Choose output file", os.getcwd(),"", "Configuration file (*.ini)|*.ini|All files (*.*)|*.*", wx.SAVE)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            fname = dlg.GetPath()
            dlg.Destroy()
        self.bank.SaveFilterList(fname)
    
    def OnFilterUpdate(self, inst=None):
        """
        
            Actions triggered by changes in filter bank.
            
            Parameters:
                inst    -    pubsub event data or wx.Event
        
        """
        self.bank.RecomputeReference()
        for x in self.bank.children:
            x.RecomputeReference()
        pub.sendMessage("filter.change", inst=self.bank)
    
    def OnFilterLeftClick(self, event = None):
        """
        
            Actions triggered by left mouse button click on filter list.
            
            Parameters:
                event    -    wx.Event
        
        """
        # either rename or enable/disable filter (if shift key is pressed)
        itm = self.list.HitTest(event.GetPosition())[0]
        if event.ShiftDown() and itm>-1: # enable/disable shift-clicked filter 
            self.OnEnableFilter(itm)
        else:
            event.Skip()
    
    def OnFilterDoubleClick(self, event = None):
        """
        
            Actions triggered by left double click on filter list.
            
            Parameters:
                event    -    wx.Event
        
        """
        # change filter properties
        if self.bank.filters[event.GetIndex()].set_filter(self):
            self.UpdateFilterDisplay()
            self.OnFilterUpdate()
        event.Skip()
    
    def OnMove(self, disp):
        """
        
            Move selected filter by given amount within list.
            
            Parameters:
                disp    -    displacement (int)
        
        """
        # move item by 'disp' positions in the list
        pos = self.list.GetFirstSelected()
        if pos+disp<0 or pos+disp>self.list.GetItemCount()-1 or pos<0: return
        itm = self.list.GetItem(pos)
        itm.SetId(pos+disp)
        self.list.DeleteItem(pos)
        self.list.InsertItem(itm)
        self.list.Select(pos+disp, True)
        p1 = self.bank.filters[pos]
        self.bank.filters[pos] = self.bank.filters[pos+disp]
        self.bank.filters[pos+disp] = p1
        self.UpdateFilterDisplay()
        self.OnFilterUpdate()
        
    def OnStartDrag(self, event = None):
        """
        
            Actions initiating a drag and drop event.
            
            Parameters:
                event    -    wx.Event
        
        """
        ds = wx.DropSource(self.list)
        p = FilterDragObject()
        p.SetData("ft")
        ds.SetData(p)
        ds.DoDragDrop(flags=wx.Drag_DefaultMove)
        
    def OnEndDrag(self, x, y, data):
        """
        
        Actions after a drag and drop event.
            
        Parameters:
            x,y    -    drop position (int)
            data   -    dropped data (str)
                        not used - assume instead that selected list item has been dragged
        
        """
        ditm = self.list.HitTest((x,y))[0]
        oitm = self.list.GetFirstSelected()
        self.OnMove(ditm-oitm)
    
    def OnFilterListRightClick(self, event = None):
        """
        
            Actions following a right mouse button click.
            
            Parameters:
                event    -    wx.Event
        
        """
        # pop up menu with filter-related actions
        menuAdd = wx.Menu()
        modules = GetModules(self.dim)
        for n in range(len(modules)): # build Add menu
            md = modules[n]()
            if md.is_visible:
                if self.bank.HasReference() and md.is_reference:
                    # don't allow adding 2 reference filters
                    pass
                else:
                    mitem = wx.MenuItem(menuAdd,id=wx.NewId(),text=modules[n].__extname__)
                    mitem.SetBitmap(modules[n]().get_icon())
                    menuAdd.AppendItem(mitem)
                    self.Bind(wx.EVT_MENU, functools.partial(self.OnAddFilter,md), id=mitem.Id)
        
        if event.EventType == wx.EVT_BUTTON.evtType[0]: # menu can be triggered by pressing + button
            # in this case, only the Add menu should appear
            self.menuPosition = self.button_add.Position
            menu = menuAdd
        else:
            menu = wx.Menu()
            self.menuPosition = event.GetPosition()
            menu.AppendSubMenu(menuAdd,"&Add...")
            mitem = menu.Append(id=wx.NewId(),text="&Remove")
            self.Bind(wx.EVT_MENU, self.OnRemoveFilter, id=mitem.Id)
            # if right-click is above an item, add enable/disable menu option
            itm = self.list.HitTest(event.GetPosition())[0]
            if itm>-1:
                if self.bank.filters[itm].is_active:
                    mitem = menu.Append(id=wx.NewId(), text="&Disable")
                else:
                    mitem = menu.Append(id=wx.NewId(), text="&Enable")
                self.Bind(wx.EVT_MENU, lambda x: self.OnEnableFilter(itm), id=mitem.Id)
            # Load/Save filter list
            mitem = menu.Append(id=wx.NewId(),text="&Load filter list")
            self.Bind(wx.EVT_MENU, self.LoadFilterList, id=mitem.Id)
            mitem = menu.Append(id=wx.NewId(),text="&Save filter list")
            self.Bind(wx.EVT_MENU, self.SaveFilterList, id=mitem.Id)
        self.PopupMenu(menu)
    
    def OnEnableFilter(self, pos):
        """
        
            Enable/Disable filter at given position.
            
            Parameters:
                pos    -    position (int)
        
        """
        # enable/disable filter
        state = not(self.bank.filters[pos].is_active)
        self.bank.filters[pos].is_active = state
        f = self.list.GetItemFont(pos)
        f.SetPointSize(10)
        if state:
            f.SetStyle(wx.FONTSTYLE_NORMAL)
        else:
            f.SetStyle(wx.FONTSTYLE_ITALIC)
        self.list.SetItemFont(pos,f)
        self.UpdateFilterDisplay()
        self.OnFilterUpdate()
    
    def OnRemoveFilter(self, event = None):
        """
        
            Actions following a filter delete request
            
            Parameters:
                event    -    wx.Event
        
        """
        # remove selected filter
        pos = self.list.GetFirstSelected()
        sels = []
        while pos>-1:
            sels.append(pos)
            pos = self.list.GetNextSelected(pos)
        for pos in sels[-1::-1]:
            ft = self.bank.filters.pop(pos)
            self.list.DeleteItem(pos)
            if ft.is_reference:
                pub.sendMessage("filter.clear_reference", inst=ft.source) # send clear reference message with ref array
        if len(sels)>0:
            # update display
            self.UpdateFilterDisplay()
            self.OnFilterUpdate()
    
    def OnAddFilter(self, ft, event = None):
        """
        
            Add given filter to current filter bank.
            
            Parameters:
                ft    -    filter (Filter)
                event -    wx.Event
        
        """
        # add filter selected in menu
        modules = GetModules(self.dim)
        idx = modules.index(ft.__class__)
        if ft.set_filter(self):
            # if filter 'set' procedure succeeded, add filter to list in adequate position
            itm = self.list.HitTest(self.menuPosition)
            if itm[0]==-1: # test if click didn't occur above an item
                pos = self.list.GetItemCount()
                if self.list.GetFirstSelected()>-1: # if not, test if one list item is selected
                    pos = self.list.GetFirstSelected()
            else: # otherwise, insert before clicked item
                pos = itm[0]
            self.list.InsertImageStringItem(pos,ft.__extname__,idx)
            self.bank.InsertFilter(pos, ft)
        # update reference plot if necessary, update display
        self.UpdateFilterDisplay()
        self.OnFilterUpdate()
    
    def SetReference(self, inst):
        """
        
            Set given array as reference.
             
            Parameters:
                inst    -    data array (DataArray)
                              or pubsub event data
        
        """
        # set reference from external source (i.e. not from filter control itself)
        # will act on currently displayed filter bank
        if not(isinstance(inst,DataArray)):
            inst = inst.data
        
        # search for existing reference
        ref_ft = None
        for ft in self.bank.filters:
            if ft.is_reference:
                ref_ft = ft
                break
        
        # if no reference, search for adequate filter and add to filter list
        if ref_ft==None:
            modules = GetModules(self.dim)
            for n in range(len(modules)):
                ft = modules[n]()
                if ft.is_reference:
                    ft.source = inst
                    self.bank.AppendFilter(ft)
                    break
        else:
            ref_ft.source = inst
        
    def RemoveReference(self, inst=None):
        """
        
            Remove reference filter, is any.
            
            Parameters:
                inst    -    pubsub event data
        
        """
        # remove reference filter
        if self.bank.RemoveReference() != None:
            self.RefreshFilters()
    
    def UpdateFilterDisplay(self, inst=None):
        """
        
            Update display of apodization window.
            
            Parameters:
                inst    -    pubsub event data
        
        """
        # update apodization filter preview
        arr = DataArray(shape=[201])
        arr.coords = [np.linspace(-1.0,1.0,201)]
        arr.data = np.ones(201) 
        is_before_ft = True
        if isinstance(self.bank,FilterBank):
            for ft in self.bank.filters:
                if ft.is_pre_filter and is_before_ft and ft.is_active:
                    ft.apply_filter(arr)
                if ft.is_transform:
                    is_before_ft = False
        data_x = np.concatenate(([-1.5,-1.0], arr.coords[0], [1.0,1.5]))
        data_y = np.concatenate(([0.0,0.0], arr.data, [0.0,0.0]))
        self.line_filter.set_data(data_x, data_y)
        self.plot_filter.draw()
