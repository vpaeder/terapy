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

    History handling classes and controls

"""

import sys
import wx
import os
from terapy import files
from terapy.core.dragdrop import HistoryDrop, HistoryDragObject
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub 
from terapy.core import icon_path
from terapy.icons import DataIconList
from terapy.core.dataman import DataArray

class HistoryMixin(object):
    """
    
        History list mix-in
        Add history functionalities to list widget
    
    """
    def __init__(self):
        """
        
            Initialization.
        
        """
        self.id = -sys.maxint
        self.map = {}
        self.ref = {}
        self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnDeleteItem)
        self.Bind(wx.EVT_LIST_DELETE_ALL_ITEMS, self.OnDeleteAllItems)
        pub.subscribe(self.BroadcastArrays, "request_arrays")
    
    def OnDeleteItem(self, event = None):
        """
        
            Actions to be taken when an item is deleted
            
            Parameters:
                event    -    wx.Event
         
        """
        try:
            del self.map[event.Data]
            self.BroadcastArrays()
        except KeyError:
            pass
        event.Skip()
    
    def OnDeleteAllItems(self, event = None):
        """
        
            Actions to be taken when all items are deleted
         
            Parameters:
                event    -    wx.Event
         
        """
        self.map.clear()
        pub.sendMessage("history.arrays", inst=[])
        event.Skip()

    def SetItemPyData(self, idp, data):
        """
        
            Associate data to item
            
            Parameters:
                idp    -    list position (int)
                data   -    data to associate (any type)
        
        """
        idx = self.GetItemData(idp)
        if idx==0:
            self.map[self.id] = data
            self.SetItemData(idp, self.id)
            self.id += 1
        else:
            self.map[idx] = data
        self.BroadcastArrays()
            
    def GetItemPyData(self, idp):
        """
        
            Return item associated to given position
            
            Parameters:
                idp    -    list position (int)
            
            Output:
                data (stored type)
        
        """
        if idp<0:
            idp = self.GetIdPosition(idp)
        return self.map[self.GetItemData(idp)]
    
    def GetArrays(self):
        """
        
            Return data associated to all items
            
            Output:
                list of data (list)
        
        """
        arrays = []
        for n in range(self.GetItemCount()):
            arr = self.GetItemPyData(n)
            arrays.append(arr)
        return arrays
    
    def BroadcastArrays(self, inst=None):
        """
        
            Broadcast data associated to all list items through pubsub
            
            Parameters:
                inst    -    pubsub event data
         
        """
        pub.sendMessage("history.arrays", inst=self.GetArrays())
    
    def GetItemById(self, idx):
        """
        
            Return data associated with given item id.
            
            Parameters:
                idx    -    item id (int)
            
            Output:
                data (any type)
        
        """
        if self.map.has_key(idx):
            return self.map.get(idx)
        else:
            return None

    def GetItemId(self, item):
        """
        
            Return item id associated with given data.
            
            Parameters:
                item    -    data (any type)
            
            Output:
                item id (int)
        
        """
        for x in self.map.iteritems():
            if x[1]==item:
                return x[0]
        return 0
    
    def GetIdPosition(self, idx):
        """
        
            Return item position associated with given item id.
            
            Parameters:
                idx    -    item id (int)
            
            Output:
                item position (int)
        
        """
        for n in range(self.GetItemCount()):
            if self.GetItemData(n) == idx:
                return n
        return -1
    
    def IsReference(self, idp):
        """
        
            Tell if item at given position is used as reference
            
            Parameters:
                idp    -    item position (int)
            
            Output:
                True/False
        
        """
        idx = self.GetItemData(idp)
        return self.ref.has_key(idx)
    
    def SetReference(self, idp, bank=None):
        """
        
            Set item at given position as reference for given filter bank
            
            Parameters:
                idp    -    item position (int)
                bank   -    filter bank (FilterBank)
        
        """
        idx = self.GetItemData(idp)
        if self.ref.has_key(idx):
            self.ref[idx].append(bank)
        else:
            self.ref[idx] = [bank]
    
    def GetReferenceBank(self, idp):
        """
        
            Get filter bank for which item at given position is reference
            
            Parameters:
                idp    -    item position (int)
            
            Output:
                filter bank (FilterBank)
        
        """
        idx = self.GetItemData(idp)
        if self.ref.has_key(idx):
            return self.ref[idx]
        else:
            return []
        
    def ClearReference(self, idp):
        """
        
            Clear reference status for item at given position
            
            Parameters:
                idp    -    item position (int)
            
            Output:
                filter bank (FilterBank)
        
        """
        idx = self.GetItemData(idp)
        if self.ref.has_key(idx):
            rf = self.ref[idx]
            del self.ref[idx]
            return rf

class HistoryList(wx.ListCtrl, HistoryMixin, ListCtrlAutoWidthMixin):
    """
    
        List widget with history functions
    
    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr):
        wx.ListCtrl.__init__(self, parent, id=id, pos=pos, size=size, style=style, validator=validator, name=name)
        HistoryMixin.__init__(self) # add history support
        ListCtrlAutoWidthMixin.__init__(self) # add auto width support
        self.setResizeColumn(0)
        
        self.SetMinSize((100,-1))
        self.InsertColumn(0,"Name")
        
        self.imglist = DataIconList()
        self.SetImageList(self.imglist,wx.IMAGE_LIST_SMALL)

class HistoryControl(wx.Panel):
    """
    
        History widget (list and control buttons)
    
    """
    def __init__(self, parent = None):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent control (wx.Window)
        
        """
        wx.Panel.__init__(self, parent)
        
        self.filter = None
        self.ref_num = 0
        
        # controls
        self.list = HistoryList(self,-1,style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.LC_NO_HEADER)
        self.list.SetMaxSize((200,-1))
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.list, 1, wx.EXPAND|wx.ALL, 2)
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
        self.SetSizer(self.sizer)
        from terapy.core.tooltip import ToolTip
        ToolTip("Double click  ->  Show/hide\nRight click   ->  Menu\nShift+Left    ->  Rename\nCtrl+Left     ->  Save as...","Usage",self.list)
        
        # bindings
        self.list.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnSelect, self.list)
        self.list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightClick, self.list)
        self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.list.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.Rename, self.list)
        self.list.Bind(wx.EVT_LIST_KEY_DOWN, self.OnKeyPress,self.list)
        self.list.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnStartDrag, self.list)
        
        self.list.SetDropTarget(HistoryDrop(self.OnEndDrag))
        
        self.button_add.Bind(wx.EVT_BUTTON,self.OnLoad,self.button_add)
        self.button_down.Bind(wx.EVT_BUTTON, lambda x:self.Move(+1),self.button_down)
        self.button_up.Bind(wx.EVT_BUTTON, lambda x:self.Move(-1),self.button_up)
        self.button_remove.Bind(wx.EVT_BUTTON,lambda x:self.Delete(self.list.GetFirstSelected()),self.button_remove)
        
        pub.subscribe(self.SetReference, 'filter.change_reference')
        pub.subscribe(self.ClearReference, 'filter.clear_reference')
        pub.subscribe(self.OnPlotDeleted, 'plot.delete')
        pub.subscribe(self.SetColors, 'plot.color_change')
        pub.subscribe(self.SetColors, 'history.need_post_process')
        pub.subscribe(self.OnLoad, 'load_data')
        pub.subscribe(self.SetCanvas, 'broadcast_canvas')
        pub.subscribe(self.SetWindow, 'broadcast_window')
    
    def Move(self, disp):
        """
        
            Move selected item by given amount
            
            Parameters:
                disp    -    displacement (int, positive or negative)
        
        """
        pos = self.list.GetFirstSelected()
        if pos+disp<0 or pos+disp>self.list.GetItemCount()-1 or pos<0: return
        rnum = self.list.GetItemData(pos)
        itm = self.list.GetItem(pos)
        arr = self.list.GetItemPyData(pos)
        itm.SetId(pos+disp)
        self.list.DeleteItem(pos)
        self.list.InsertItem(itm)
        self.list.SetItemPyData(pos+disp,arr)
        self.list.Select(pos+disp)
        if self.ref_num == rnum:
            self.ref_num = self.list.GetItemData(pos+disp)

    def OnStartDrag(self, event = None):
        """
        
            Actions triggered by drag event.
            
            Parameters:
                event    -    wx.Event
        
        """
        pos = self.list.GetFirstSelected()
        ev = self.list.GetItemPyData(pos)
        # broadcast data
        pub.sendMessage("history.drag_object", inst=ev)
        ds = wx.DropSource(self.list)
        p = HistoryDragObject()
        p.SetData(ev)
        ds.SetData(p)
        ds.DoDragDrop(flags=wx.Drag_DefaultMove)
        
    def OnEndDrag(self, x, y, data):
        """
        
            Actions following drop on control.
            
            Parameters:
                x,y    -    coordinates of drop action (int)
                data   -    dropped data (str)
                            Passing drag and drop data in wxpython is incovenient.
                            Alternative used here: use GetFirstSelected and HitTest functions
                            of wx.ListBox to determine what to move and where to put it
         
        """
        ditm = self.list.HitTest((x,y))[0]
        oitm = self.list.GetFirstSelected()
        self.Move(ditm-oitm)
            
    def OnLoad(self, event):
        """
        
            Actions triggered by load event.
            
            Parameters:
                event    -    wx.Event
        
        """
        # load previous scan data 
        dialog = wx.FileDialog(self, "Choose input file", os.getcwd(),"", files.read_wildcards(), wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            # actualize canvas reference
            pub.sendMessage('request_canvas')
            #
            pub.sendMessage("set_status_text",inst="Loading old scan data...")
            for ff in files.modules:
                data = None
                try:
                    data = ff().read(dialog.GetPath())
                except:
                    pass
                if data!=None:
                    break
            for x in data:
                # fix axes list in case it isn't the right length
                if len(x.axes)<len(x.shape):
                    x.axes.extend([None]*(len(x.shape)-len(x.axes)))
                elif len(x.axes)>len(x.shape):
                    x.axes = x.axes[:len(x.shape)]
                # add plot entry to list
                self.list.InsertImageStringItem(0,x.name,len(x.shape))
                self.list.SetItemPyData(0,x)
                # add plot to appropriate plot canvas
                x.plot = self.canvas.AddPlot(array=x)
                if len(x.shape)==2: # 2D
                    x.plot.SetName(x.name)
                pub.sendMessage("plot.color_change")
                #pub.sendMessage("history.post_process",data=x)
        pub.sendMessage("set_status_text",inst="Finished!")
        dialog.Destroy()

    def SetCanvas(self, inst):
        """
        
            Set canvas reference from pubsub event.
            
            Parameters:
                inst    -    pubsub event data
        
        """
        self.canvas = inst
    
    def SetWindow(self, inst):
        """
        
            Set main window reference from pubsub event.
            
            Parameters:
                inst    -    pubsub event data
        
        """
        self.window = inst
    
    def OnKeyPress(self, event=None):
        """
        
            Actions triggered by key press on control.
            
            Parameters:
                event    -    wx.Event
        
        """
        if event.KeyCode==8 or event.KeyCode==127: # del or backspace
            self.Delete(event.GetIndex())
        else:
            event.Skip()
    
    def OnSelect(self, event=None):
        """
        
            Actions triggered by double click on list item.
            
            Parameters:
                event    -    wx.Event
        
        """
        # show/hide plot
        array = self.list.GetItemPyData(event.GetIndex())
        if array.plot!=None: # a plot exists, must be removed
            array.plot.Delete()
            array.plot = None
        else:
            # actualize canvas reference
            pub.sendMessage('request_canvas')
            array.plot = self.canvas.AddPlot(target="current",array=array)
        pub.sendMessage("plot.color_change")
    
    def OnPlotDeleted(self, event=None):
        """
        
            Actions triggered on item delete event.
            
            Parameters:
                event    -    wx.Event
        
        """
        if event.data==None: return
        for n in range(self.list.GetItemCount()):
            arr = self.list.GetItemPyData(n)
            if arr.plot==event.data:
                arr.plot.Delete()
    
    def OnLeftClick(self, event = None):
        """
        
            Actions triggered by left click on list item.
        
            Parameters:
                event    -    wx.Event
         
        """
        itm = self.list.HitTest(event.GetPosition())[0]
        if event.ShiftDown() and itm>-1: # rename clicked item 
            self.list.EditLabel(itm)
        elif event.ControlDown() and itm>-1: # save clicked item as
            self.SaveAs(itm)
        else:
            event.Skip()
        
    def OnRightClick(self, event = None):
        """
        
            Actions triggered by right click on list item.
            
            Parameters:
                event    -    wx.Event
        
        """
        # show menu
        if event.GetEventType() == wx.EVT_RIGHT_DOWN.evtType[0]:
            if self.list.HitTest(event.GetPosition())[0]>-1:
                # right click on a history item => handled by specific event
                event.Skip()
                return
            else:
                # right click in list but not on list entry => only Load available 
                menu = wx.Menu()
                itm = menu.Append(wx.NewId(), "&Load scan")
                self.Bind(wx.EVT_MENU, self.OnLoad, id=itm.Id)
                self.PopupMenu(menu)
                return
        # right click on list item
        menu = wx.Menu()
        itm = menu.Append(wx.NewId(), "&Load scan")
        self.Bind(wx.EVT_MENU, self.OnLoad, id=itm.Id)
        if event.GetIndex()>-1:
            arr = self.list.GetItemPyData(event.GetIndex())
            # create menu entries for operations on item
            itm = menu.Append(wx.NewId(), "&Rename")
            self.Bind(wx.EVT_MENU, lambda x: self.list.EditLabel(event.GetIndex()), id=itm.Id)
            itm = menu.Append(wx.NewId(), "&Delete")
            self.Bind(wx.EVT_MENU, lambda x: self.Delete(event.GetIndex()), id=itm.Id)
            itm = menu.Append(wx.NewId(), "&Save as...")
            self.Bind(wx.EVT_MENU, lambda x: self.SaveAs(event.GetIndex()), id=itm.Id)
            # if array has a xml image of event tree, propose reload
            if hasattr(arr,'xml'):
                itm = menu.Append(wx.NewId(),"Reload event tree")
                self.Bind(wx.EVT_MENU, lambda x: pub.sendMessage("history.reload_events", string=arr.xml), id=itm.Id)
            # specific menu entries for 1D plot
            if len(arr.shape) == 1:
                itm = menu.Append(wx.NewId(), "Change c&olor")
                self.Bind(wx.EVT_MENU, lambda x: self.ChangeColour(event.GetIndex()), id=itm.Id)
                if arr.color!=None:
                    itm = menu.Append(wx.NewId(), "Reset c&olor")
                    self.Bind(wx.EVT_MENU, lambda x: self.ResetColour(event.GetIndex()), id=itm.Id)
                if not(hasattr(self,"window")):
                    pub.sendMessage("request_top_window")
                if not(self.window.is_scanning) or event.GetIndex()>0:
                    if not(hasattr(self,"canvas")):
                        pub.sendMessage("request_canvas")
                    if self.list.IsReference(event.GetIndex()):
                        itm = menu.Append(wx.NewId(), "&Clear reference")
                        self.Bind(wx.EVT_MENU, self.ClearReference, id=itm.Id)
                    if self.canvas.CurrentPage.is_filter:
                        itm = menu.Append(wx.NewId(), "S&et as reference")
                        self.Bind(wx.EVT_MENU, lambda x: self.SetReference(event.GetIndex()), id=itm.Id)
            
        self.PopupMenu(menu)

    def ResetColour(self, position):
        """
        
            Reset colour of selected item.
            
            Parameters:
                position    -    item position (int)
        
        """
        arr = self.list.GetItemPyData(position)
        arr.color = None
        if arr.plot!=None:
            arr.plot.SetPlotColors()
            arr.plot.Update()
                
    def ChangeColour(self, position):
        """
        
            Ask user to select colour of selected item.
            
            Parameters:
                position    -    item position (int)
        
        """
        arr = self.list.GetItemPyData(position)
        data = wx.ColourData()
        if arr.plot!=None:
            col = arr.plot.GetColor()
        else:
            col = wx.Colour(0,0,0)
        data.SetColour(col)
        dlg = wx.ColourDialog(self,data)
        if dlg.ShowModal()==wx.ID_OK:
            data = dlg.GetColourData()
            arr.color = data.GetColour()
            col = arr.color
            if arr.plot!=None:
                self.list.SetItemTextColour(position,col)
                arr.plot.SetPlotColors()
                arr.plot.Update()
        dlg.Destroy()

    def Delete(self, position):
        """
        
            Delete selected item.
            
            Parameters:
                position    -    item position (int)
        
        """
        # delete selected list entry
        if position<0 or position>self.list.GetItemCount()-1: return
        arr = self.list.GetItemPyData(position)
        # if a plot is associated, remove plot
        if arr.plot!=None:
            if self.ref_num == self.list.GetItemData(position): self.ClearReference()
            arr.plot.Delete()
        self.list.DeleteItem(position)

    def Insert(self,arr,name="Current scan", pos=0):
        """
        
            Insert new item in given position.
            
            Parameters:
                arr         -    data array (DataArray)
                name        -    displayed name (str)
                pos         -    item position (int)
        
        """
        # insert new entry in history list, at position pos, associated with data array 'arr'
        # build list of existing names
        nm = []
        for n in range(self.list.GetItemCount()):
            nm.append(self.list.GetItemText(n))
        # check that proposed name doesn't exist
        ext = ""
        n = 0
        while nm.count(name+ext)>0:
            ext = " " + str(n)
            n+=1
        name = name + ext
        # insert item
        self.list.InsertImageStringItem(pos,name,len(arr.shape))
        self.list.SetItemPyData(0,arr)
        # return modified name
        return name
    
    def SetReference(self, inst):
        """
        
            Set selected item as reference.
            
            Parameters:
                inst    -    item position (int)
                             or pubsub data (DataArray)
        
        """
        if not(isinstance(inst,int)):
            if isinstance(inst,DataArray):
                for n in range(self.list.GetItemCount()):
                    arr = self.list.GetItemPyData(n)
                    if arr == inst:
                        position = n
                        break
            message = 'history.change_reference'
        else:
            message = 'history.set_reference'
        self.TagAsReference(inst)
        arr = self.list.GetItemPyData(inst)
        pub.sendMessage(message, inst=arr)
    
    def TagAsReference(self, position, state=True):
        """
        
            Tag/Untag selected item as reference.
            
            Parameters:
                position    -    item position (int)
                state       -    state (bool)
        
        """
        if state:
            if not(hasattr(self,"canvas")):
                pub.sendMessage("request_canvas")
            if self.canvas.CurrentPage.is_filter:
                # check if a reference exists in current filter bank
                for n in range(self.list.GetItemCount()):
                    if self.list.IsReference(n):
                        if self.canvas.CurrentPage.bank in self.list.GetReferenceBank(n):
                            self.list.ClearReference(n)
                            self.list.SetItemImage(n,1)
                # set reference to given position
                self.list.SetReference(position, self.canvas.CurrentPage.bank)
                self.list.SetItemImage(position,4)
        else:
            self.list.ClearReference(position)
            self.list.SetItemImage(position,1)
    
    def ClearReference(self, inst=None):
        """
        
            Clear reference status of selected item.
             
            Parameters:
                inst    -    wx.Event or pubsub data (DataArray)
        
        """
        if isinstance(inst,wx.Event): # action came from menu
            idp = self.list.GetFirstSelected()
        else: # action came from external source through pubsub
            idp = -1
            for n in range(self.list.GetItemCount()):
                if self.list.GetItemPyData(n) == inst:
                    idp = n
                    break
        if idp>-1:
            self.list.SetItemImage(idp,1)
            pub.sendMessage('history.clear_reference',inst=self.list.GetReferenceBank(idp))
            self.list.ClearReference(idp)
    
    def SaveAs(self, position):
        """
        
            Trigger save procedure for selected item.
            
            Parameters:
                position    -    item position (int)
        
        """
        dlg = wx.FileDialog(self, "Choose output file", os.getcwd(), "", files.save_wildcards(allfiles=False), wx.SAVE | wx.CHANGE_DIR)
        
        if dlg.ShowModal() == wx.ID_OK:
            arr = self.list.GetItemPyData(position)
            flt = files.modules[dlg.GetFilterIndex()]()
            flt.save(dlg.GetPath(),self.list.GetItemPyData(position))
            plt = arr.plot
            n = 0
            while len(plt.children)>0:
                if flt.multi_data: 
                    flt.save(dlg.GetPath(),plt.children[0].GetData(),name="PP_"+str(n))
                else:
                    path = dlg.GetPath().split(".")
                    path[-2] = path[-2] + "_PP_" + str(n)
                    path = ".".join(path)
                    flt.save(path,plt.children[0].GetData())
                n+=1
                plt = plt.children[0]
        dlg.Destroy()

    def Rename(self, event = None):
        """
        
            Rename selected item.
            
            Parameters:
                event    -    wx.Event
        
        """
        idx = event.GetIndex()
        if len(event.Text)==0:
            event.Veto() # don't allow empty name
            return
        arr = self.list.GetItemPyData(idx)
        if arr.filename!="":
            fname = arr.filename.split(".")
            ext = fname[-1]
            newname = os.path.normcase(os.path.dirname(".".join(fname)) + os.path.normcase('/') + event.Text + "." + ext)
            if os.path.exists(newname):
                event.Veto() # don't overwrite an existing file
            else:
                os.rename(arr.filename, newname)
                # search for all plots that share the same file name
                oldname = arr.filename
                for n in range(self.list.GetItemCount()):
                    arrb = self.list.GetItemPyData(n)
                    if arrb.filename == oldname:
                        arrb.filename = newname
                # rename array and update plot if necessary
                arr.name = event.Text
                if arr.plot!=None: arr.plot.SetName(arr.name)
                
    def SetColors(self, event = None):
        """
        
            Set colors of items in list from associate data arrays.
            
            Parameters:
                event    -    wx.Event
        
        """
        Ng = self.list.GetItemCount()
        for n in range(Ng):
            array = self.list.GetItemPyData(n)
            f = self.list.GetItemFont(n)
            f.SetPointSize(10)
            f.SetWeight(wx.FONTWEIGHT_NORMAL)
            col = wx.Colour(0,0,0)
            if array.plot!=None:
                f.SetWeight(wx.FONTWEIGHT_BOLD)
                col = array.plot.GetColor()
            self.list.SetItemTextColour(n,col)
            self.list.SetItemFont(n,f)
