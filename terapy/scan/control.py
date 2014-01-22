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

    Scan control widget

"""
    
from terapy.scan.base import ScanEvent, PropertyNode
from terapy.core.dataman import Measurement
from terapy.core.treectrl import TreeCtrl, SubTree
from terapy.core.threads import ScanThread
from terapy.core.button import RunButton
from terapy.core.parsexml import ParseAttributes
from terapy.core.dragdrop import EventDrop, EventDragObject
from terapy.core import icon_path, event_file
from terapy.scan import modules
import wx
import os
import functools
from time import sleep
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub

class ScanEventList(wx.Panel):
    """
    
        Scan control widget
    
    """
    def __init__(self, parent = None):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
        
        """
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.events = []
        self.scanThread = None
        
        # event list
        self.list_events = TreeCtrl(self, -1, style=wx.TR_EDIT_LABELS|wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_SINGLE|wx.TR_LINES_AT_ROOT)
        from terapy.core.tooltip import ToolTip
        ToolTip("Double click  ->  Change properties\nRight click   ->  Menu\nShift+Left    ->  Enable/disable","Usage",self.list_events)
        self.img_list = wx.ImageList(16,16)
        self.list_events.SetMaxSize((200,-1))
        self.list_events.SetMinSize((200,-1))
        
        for x in modules:
            self.img_list.Add(x(self).get_icon())
        
        self.list_events.SetImageList(self.img_list)
        
        # controls
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.list_events, 1, wx.EXPAND|wx.TOP, 2)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.button_up = wx.BitmapButton(self, -1, wx.Image(icon_path + "go-up.png").ConvertToBitmap())
        self.button_down = wx.BitmapButton(self, -1, wx.Image(icon_path + "go-down.png").ConvertToBitmap())
        self.button_add = wx.BitmapButton(self, -1, wx.Image(icon_path + "list-add.png").ConvertToBitmap())
        self.button_remove = wx.BitmapButton(self, -1, wx.Image(icon_path + "list-remove.png").ConvertToBitmap())
        self.button_run = RunButton(self, -1)
        hbox.Add(self.button_up, 0, wx.EXPAND|wx.ALL, 2)
        hbox.Add(self.button_down, 0, wx.EXPAND|wx.ALL, 2)
        hbox.Add(self.button_add, 0, wx.EXPAND|wx.ALL, 2)
        hbox.Add(self.button_remove, 0, wx.EXPAND|wx.ALL, 2)
        hbox.Add(self.button_run, 0, wx.EXPAND|wx.ALL, 2)
        self.sizer.Add(hbox, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 2)
        
        # bindings
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnEventListRightClick, self.list_events)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnEventDoubleClick, self.list_events)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnEditTreeLabel, self.list_events)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEditTreeLabel, self.list_events)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnStartDrag, self.list_events)
        self.list_events.Bind(wx.EVT_RIGHT_DOWN, self.OnEventListRightClick)
        self.list_events.Bind(wx.EVT_LEFT_DOWN, self.OnEventLeftClick)
        self.Bind(wx.EVT_BUTTON, self.OnButtonUp, self.button_up)
        self.Bind(wx.EVT_BUTTON, self.OnButtonDown, self.button_down)
        self.Bind(wx.EVT_BUTTON, self.OnEventListRightClick, self.button_add)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveEvent, self.button_remove)
        self.Bind(wx.EVT_BUTTON, self.OnButtonRun, self.button_run)
        pub.subscribe(self.OnStopMeasurement, "scan.after")
        pub.subscribe(self.ParseXMLFromString, "history.reload_events")

        self.list_events.SetDropTarget(EventDrop(self.OnEndDrag))
        
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.sizer.SetSizeHints(self)
        
        self.DefaultEvents()
        
    def ParseXMLTree(self, tree):
        """
        
            Parse given XML tree and build ScanEvent structure.
             
            Parameters:
                tree    -    minidom XML document
            
            Output:
                nested list of ScanEvent
        
        """
        ml = [x.__name__ for x in modules] # list of module names
        cn = [] # current tree branch
        for x in tree:
            if hasattr(x,'tagName'):
                if x.tagName == 'item':
                    attrs = x.attributes
                    if attrs.has_key('class'):
                        if ml.count(attrs['class'].value)>0:
                            idx = ml.index(attrs['class'].value)
                            cn.append(modules[idx](self.list_events))
                            ParseAttributes(attrs,cn[-1])
                if x.hasChildNodes():
                    cn.append(self.ParseXMLTree(x.childNodes))
        return cn
    
    def BuildXMLTree(self, itm, root=None, doc=None):
        """
        
            Build XML tree out of given TreeCtrl subtree.
            
            Parameters:
                itm    -    TreeCtrl item (wx.TreeItem)
                root   -    recipient minidom XML node 
                doc    -    recipient minidom XML document
        
        """
        if doc == None:
            from xml.dom import minidom
            doc = minidom.Document()
            croot = doc.createElement("config")
            croot.attributes["scope"] = "events"
            doc.appendChild(croot)
            root = doc.createElement("events")
            croot.appendChild(root)
        ev = self.list_events.GetItemPyData(itm)
        p = doc.createElement("item")
        root.appendChild(p)
        p.attributes["name"] = self.list_events.GetItemText(itm)
        p.attributes["class"] = ev.__class__.__name__
        for x in ev.config:
            p.attributes[x] = str(getattr(ev,x))
                
        if self.list_events.ItemHasChildren(itm):
            children = self.list_events.GetItemChildren(itm, ScanEvent)
            for x in children:
                self.BuildXMLTree(x, p, doc)
        return doc
    
    def CreateEventTree(self,tree,root=None):
        """
        
            Fill in TreeCtrl with given ScanEvent tree.
            
            Parameters:
                tree    -    nested list of ScanEvent
                root    -    root tree item (wx.TreeItem, root item if None)
        
        """
        if root==None:
            root = self.list_events.GetRootItem()
        nitm = root
        for x in tree:
            if isinstance(x,ScanEvent):
                nitm = self.InsertItem(x,root,False)
                self.list_events.SetItemText(nitm,x.name)
            else:
                self.CreateEventTree(x, nitm)
        
    def DefaultEvents(self):
        """
        
            Fill TreeCtrl with default events.
            Load default events from event_file if present.
        
        """
        self.list_events.DeleteAllItems()
        root = self.list_events.AddRoot("Scan events")
        if event_file==None: return # no event_file defined
        if os.path.exists(event_file):
            from xml.dom import minidom
            elist = [] 
            xmldoc = minidom.parse(event_file).getElementsByTagName('events')
            elist = self.ParseXMLTree(xmldoc)
            self.CreateEventTree(elist[0],root)

    def InsertItem(self, ev, root = None, expand=True):
        """
        
            Insert given event in tree.
            
            Parameters:
                ev        -    event to insert (ScanEvent)
                root      -    parent item (wx.TreeItem, root item if None)
                expand    -    if True, expand parent folder
        
        """
        if root == None:
            root = self.list_events.GetRootItem()
        nitm = self.list_events.AppendItem(root,ev.__extname__)
        idx = modules.index(ev.__class__)
        self.list_events.SetItemImage(nitm,idx)
        f = self.list_events.GetItemFont(nitm)
        f.SetPointSize(10)
        f.SetWeight(wx.FONTWEIGHT_BOLD)
        self.list_events.SetItemFont(nitm,f)
        self.list_events.SetItemPyData(nitm,ev)
        if expand:
            self.list_events.Expand(root)
        ev.refresh()
        ev.populate()
        return nitm
        
    def OnEditTreeLabel(self, event = None):
        """
        
            Actions triggered by edit label request.
            
            Parameters:
                event    -    wx.Event
        
        """
        itm = event.GetItem()
        ev = self.list_events.GetItemPyData(itm)
        if not(isinstance(ev,ScanEvent)): # if not event object, find parent event object
            while not(isinstance(ev,ScanEvent)):
                itm = self.list_events.GetItemParent(itm)
                ev = self.list_events.GetItemPyData(itm)
            itm0 = event.GetItem()
            propNode = self.list_events.GetItemChildren(itm, PropertyNode)[0] # get property node
            if itm0 == propNode:
                event.Veto()
                if self.list_events.IsExpanded(itm0):
                    self.list_events.Collapse(itm0)
                else:
                    self.list_events.Expand(itm0)
                return # can't edit "Properties" tag
            else: # edit with associated editor
                p = self.list_events.GetItemChildren(propNode).index(itm0)
                self.list_events.SetItemText(itm0, str(ev.propNodes[p]))
                self.list_events.SetItemPyData(itm0,[ev,p])
                ev.edit_label(event,p)
        else: # if event object, name can be edited as is
            event.Skip()
            
    def OnEndEditTreeLabel(self, event = None):
        """
        
            Actions following label edition.
            
            Parameters:
                event    -    wx.Event
        
        """
        itm = event.GetItem()
        ev = self.list_events.GetItemPyData(itm)
        if isinstance(ev,list): # the edited item is a property node
            event.Veto()
            self.list_events.SetItemPyData(itm,None)
            ev[0].set_property(ev[1],event.GetLabel())
        elif isinstance(ev,ScanEvent):
            ev.name = event.GetLabel()
        else:
            event.Skip()
        itm = self.list_events.GetNextSibling(itm)
        if itm.IsOk():
            self.list_events.SelectItem(itm)
        self.SetFocus()
    
    def OnEventLeftClick(self, event = None):
        """
        
            Actions triggered by left mouse button click on tree item.
            
            Parameters:
                event    -    wx.Event
        
        """
        itm = self.list_events.HitTest(event.GetPosition())[0]
        if event.ShiftDown() and itm>-1: # enable/disable shift-clicked event 
            self.OnEnableEvent(itm)
        else:
            event.Skip()
    
    def OnEventDoubleClick(self, event = None):
        """
        
            Actions triggered by left mouse button double click on tree item.
            
            Parameters:
                event    -    wx.Event
        
        """
        ev = self.list_events.GetItemPyData(event.GetItem())
        if hasattr(ev,'is_root'):
            if ev.is_root:
                self.list_events.EditLabel(event.GetItem())
                return
        if hasattr(ev,'set'):
            if ev.set():
                ev.populate()
        else:
            self.list_events.EditLabel(event.GetItem())
        
    def OnEventListRightClick(self, event = None):
        """
        
            Actions triggered by right mouse button click on tree item.
            
            Parameters:
                event    -    wx.Event
        
        """
        if event.EventType == wx.EVT_BUTTON.evtType[0]:
            self.menuPosition = self.button_add.Position
        else:
            self.menuPosition = event.GetPosition()
        
        itm = self.list_events.HitTest(self.menuPosition)[0]
        menu = wx.Menu()
        menuAdd = wx.Menu()
        
        for n in range(len(modules)):
            obj = modules[n](self.list_events)
            mitem = wx.MenuItem(menuAdd,id=wx.NewId(),text=obj.__extname__)
            mitem.SetBitmap(obj.get_icon())
            if obj.is_root and not(itm.IsOk()) and obj.is_visible:
                menuAdd.AppendItem(mitem)
                self.Bind(wx.EVT_MENU, functools.partial(self.OnAddEvent,obj), id=mitem.Id)
            elif itm.IsOk() and obj.is_visible:
                ev = self.list_events.GetItemPyData(itm)
                if isinstance(ev,ScanEvent):
                    if (ev.is_loop or ev.is_root) and not(obj.is_root):
                        menuAdd.AppendItem(mitem)
                        self.Bind(wx.EVT_MENU, functools.partial(self.OnAddEvent,obj), id=mitem.Id)
        
        if menuAdd.GetMenuItemCount()>0:
            menu.AppendSubMenu(menuAdd,"&Add...")
        
        if self.list_events.GetItemPyData(self.list_events.Selection)!=None or itm.IsOk():
            mitem = menu.Append(id=wx.NewId(),text="&Remove")
            self.Bind(wx.EVT_MENU, self.OnRemoveEvent, id=mitem.Id)
            mitem = menu.Append(id=wx.NewId(),text="&Rename")
            self.Bind(wx.EVT_MENU, lambda x: self.list_events.EditLabel(self.list_events.Selection), id=mitem.Id)
        # if right-click is above an item, add enable/disable menu option
        if itm.IsOk():
            ev = self.list_events.GetItemPyData(itm)
            if not(hasattr(ev, "is_active")):
                return # not an editable menu item
            # fill replace options with similar items
            menuRep = wx.Menu()
            for n in range(len(modules)):
                obj = modules[n]()
                mitem = wx.MenuItem(menuRep,id=wx.NewId(),text=obj.__extname__)
                mitem.SetBitmap(obj.get_icon())
                self.Bind(wx.EVT_MENU, functools.partial(self.OnReplaceEvent,ev,obj), id=mitem.Id)
                if obj.is_visible:
                    if (ev.is_loop and obj.is_loop) or (ev.is_input and obj.is_input) or (ev.is_save and obj.is_save) or (ev.is_display and obj.is_display):
                        menuRep.AppendItem(mitem)
            if menuRep.GetMenuItemCount()>0:
                menu.AppendSubMenu(menuRep, "Replace &with...")
            
            if not(ev.is_root):
                if self.list_events.GetItemPyData(itm).is_active:
                    mitem = menu.Append(id=wx.NewId(), text="&Disable")
                else:
                    mitem = menu.Append(id=wx.NewId(), text="&Enable")
                self.Bind(wx.EVT_MENU, lambda x: self.OnEnableEvent(itm), id=mitem.Id)
            
        menu.AppendSeparator()
        mitem = menu.Append(id=wx.NewId(),text="&Load sequence")
        self.Bind(wx.EVT_MENU, lambda x: self.OnLoadSequence(itm), id=mitem.Id)
        
        if itm.IsOk():
            if ev.is_root:
                mitem = menu.Append(id=wx.NewId(),text="&Save sequence")
                self.Bind(wx.EVT_MENU, lambda x: self.OnSaveSequence(itm), id=mitem.Id)
                menu.AppendSeparator()
                mitem = menu.Append(id=wx.NewId(),text="&Run sequence")
                self.Bind(wx.EVT_MENU, lambda x: self.OnRunSequence(itm), id=mitem.Id)
             
        self.PopupMenu(menu)
        menu.Destroy()

    def OnLoadSequence(self, itm):
        """
        
            Actions triggered by load ScanEvent sequence request.
            
            Parameters:
                event    -    wx.Event
        
        """
        dialog = wx.FileDialog(self, "Choose input file", os.getcwd(),"", "Configuration file (*.ini)|*.ini|All files (*.*)|*.*", wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            from xml.dom import minidom
            root = self.list_events.GetRootItem()
            xmldoc = minidom.parse(dialog.GetPath()).getElementsByTagName('events')
            elist = self.ParseXMLTree(xmldoc)
            self.CreateEventTree(elist[0],root)
            itm = self.list_events.FindItem(elist[0][0], root)
            self.list_events.CollapseAll() # collapse tree
            self.Unfold(-1, itm) # unfold newly added sequence
            dialog.Destroy()
    
    def ParseXMLFromString(self, string):
        """
        
            Parse XML tree represented as text string and add result to tree.
            
            Parameters:
                string    -    XML tree in string format (str)
        
        """
        if not(isinstance(string,str)):
            string = string.data
        from xml.dom import minidom
        xmldoc = minidom.parseString(string).getElementsByTagName('events')
        elist = self.ParseXMLTree(xmldoc)
        root = self.list_events.GetRootItem()
        self.CreateEventTree(elist[0],root)
        itm = self.list_events.FindItem(elist[0][0], root)
        self.list_events.CollapseAll() # collapse tree
        self.Unfold(-1, itm) # unfold newly added sequence
    
    def OnSaveSequence(self, itm):
        """
        
            Actions following save sequence request for given item.
            
            Parameters:
                itm    -    tree item (wx.TreeItem)
        
        """
        dialog = wx.FileDialog(self, "Choose output file", os.getcwd(),"", "Configuration file (*.ini)|*.ini|All files (*.*)|*.*", wx.SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            doc = self.BuildXMLTree(itm)
            f = open(dialog.GetPath(),'w')
            doc.writexml(f,indent="  ", addindent="  ", newl="\n")
            f.close()
            dialog.Destroy()

    def OnReplaceEvent(self, old, new, event):
        """
        
            Replace given item by new item.
            
            Parameters:
                old    -    item to replace (ScanEvent)
                new    -    item to replace with (ScanEvent)
                event  -    wx.Event
        
        """
        for x in new.config:
            try:
                setattr(new,x,getattr(old,x))
            except:
                pass
        new.host = old.host
        itm = self.list_events.FindItem(old)
        self.list_events.SetItemPyData(itm,new)
        new.name = new.__extname__
        self.list_events.SetItemText(itm,new.name)
        new.refresh()
        new.create_property_root()
        new.populate()
    
    def RefreshEvents(self, subtree=None):
        """
        
            Refresh given subtree.
            
            Parameters:
                subtree    -    subtree to be refreshed (SubTree, whole tree if None)
        
        """
        if subtree==None:
            subtree = self.list_events.GetItemSubTree(self.list_events.GetRootItem(),ScanEvent)
        if isinstance(subtree.data,ScanEvent):
            subtree.data.refresh()
            subtree.data.populate()
        if isinstance(subtree,SubTree):
            for x in subtree.items:
                self.RefreshEvents(x)
    
    def Unfold(self, lvl=-1, itm=None):
        """
        
            Unfold given tree item.
            
            Parameters:
                lvl    -    number of levels to unfold (int, if -1 unfold all)
                itm    -    tree item (wx.TreeItem, root item if None)
        
        """
        if lvl==0:
            return
        if itm==None:
            itm = self.list_events.GetRootItem()
        if itm.IsOk():
            self.list_events.Expand(itm)
            if self.list_events.ItemHasChildren(itm):
                for x in self.list_events.GetItemChildren(itm):
                    self.Unfold(lvl-1,x)
    
    def UnfoldSequence(self, n=0):
        """
        
            Unfold given scan sequence.
            
            Parameters:
                n    -    scan sequence index (int)
        
        """
        try:
            self.list_events.CollapseAll()
        except:
            pass
        root = self.list_events.GetRootItem()
        itm, cookie = self.list_events.GetFirstChild(root)
        while itm.IsOk():
            if self.list_events.ItemHasChildren(itm):
                try:
                    self.list_events.ExpandAllChildren(itm)
                except:
                    pass
                break
            itm, cookie = self.list_events.GetNextChild(root,cookie)
    
    def CheckValidity(self, stree, meas):
        """
        
            Check validity of given scan sequence wrt given measurement structure.
            
            Parameters:
                stree    -    scan sequence (SubTree)
                meas     -    measurement structure (Measurement)
        
        """
        is_valid = True
        if isinstance(stree.data,ScanEvent):
            if stree.data.m_id < meas.count:
                is_valid = is_valid and stree.data.check_validity(meas.data[stree.data.m_id])
                self.plot_or_save[stree.data.m_id] = (self.plot_or_save[stree.data.m_id] or stree.data.is_save or stree.data.is_display)
                if stree.data.is_input and self.plot_or_save[stree.data.m_id]:
                    return False # can't plot or save before recording data
        if isinstance(stree,SubTree):
            for x in stree.items:
                is_valid = is_valid and self.CheckValidity(x,meas)
        return is_valid
    
    def OnRunSequence(self, itm):
        """
        
            Actions initiating a sequence run.
            
            Parameters:
                itm    -    root item for sequence (wx.TreeItem)
        
        """
        # refresh events
        self.RefreshEvents()
        
        # initialize data tree
        stree = self.list_events.GetItemSubTree(itm, ScanEvent)
        ev = self.list_events.GetItemPyData(itm)
        meas = Measurement(stree.data.name,stree)
        meas.BuildDataTree()
        
        # check that events work with associated data
        self.plot_or_save = [False]*meas.count
        if not(self.CheckValidity(stree,meas)):
            print "Invalid event tree!"
            return
        del self.plot_or_save
        
        # store event tree in XML format
        doc = self.BuildXMLTree(itm)
        meas.xml = doc.toprettyxml(indent="  ", newl="\n")
        
        # store system state (state of instruments before measurement)
        from terapy import hardware
        doc = hardware.get_system_state()
        meas.systemState = doc.toprettyxml(indent="  ", newl="\n")
        
        # disable controls
        self.ToggleControls(False)
        
        # announce measurement start
        pub.sendMessage("scan.start", inst=meas)
        
        self.scanThread = ScanThread(ev, meas)
        self.scanThread.start()
        
    def OnEnableEvent(self, itm):
        """
        
            Actions following enable/disable given scan event.
            
            Parameters:
                itm    -    tree item (wx.TreeItem)
        
        """
        ev = self.list_events.GetItemPyData(itm)
        ev.is_active = not(ev.is_active)
        f = self.list_events.GetItemFont(itm)
        f.SetPointSize(10)
        if ev.is_active:
            #f.SetWeight(wx.FONTWEIGHT_BOLD)
            f.SetStyle(wx.FONTSTYLE_NORMAL)
        else:
            #f.SetWeight(wx.FONTWEIGHT_NORMAL)
            f.SetStyle(wx.FONTSTYLE_ITALIC)
        self.list_events.SetItemFont(itm,f)

    def OnRemoveEvent(self, event = None):
        """
        
            Actions following tree item delete request.
            
            Parameters:
                event    -    wx.Event
        
        """
        pos = self.list_events.Selection
        if pos.IsOk():
            ev = self.list_events.GetItemPyData(pos)
            if isinstance(ev,ScanEvent): # delete only items linked with a ScanEvent object
                self.list_events.Delete(pos)
    
    def OnAddEvent(self, ev, event):
        """
        
            Actions following scan event add request.
            
            Parameters:
                ev    -    scan event to be added (ScanEvent)
                event -    wx.Event
        
        """
        if ev.set():
            itm = self.list_events.HitTest(self.menuPosition)[0]
            if not(itm.IsOk()):
                itm = self.list_events.GetRootItem()
            self.InsertItem(ev, itm)

    def OnStartDrag(self, event = None):
        """
        
            Actions following beginning of drag action.
            
            Parameters:
                event    -    wx.Event
        
        """
        pos = event.GetItem()
        ev = self.list_events.GetItemPyData(pos)
        if isinstance(ev,ScanEvent):
            self.drag_object = pos
            ds = wx.DropSource(self.list_events)
            p = EventDragObject()
            p.SetData(self.drag_object)
            ds.SetData(p)
            ds.DoDragDrop(flags=wx.Drag_DefaultMove)
                
    def OnEndDrag(self, x, y, data):
        """
        
            Actions following drop on TreeCtrl.
            
            Parameters:
                x,y    -    coordinates of drop action (int)
                data   -    dropped data (str)
                            Passing drag and drop data in wxpython is incovenient.
                            Alternative used here: data is stored as self.drag_object
        
        """
        ditm = self.list_events.HitTest((x,y))[0]
        if not(ditm.IsOk()): return # not dropped on a tree entry
        # store dropped item
        oitm = self.drag_object
        stree = self.list_events.GetItemSubTree(oitm)
        # target item
        ev = self.list_events.GetItemPyData(ditm)
        
        if not(isinstance(ev, ScanEvent)):
            # target is not a ScanEvent instance, search for previous ScanEvent entry
            titm = ditm
            while titm.IsOk():
                if self.list_events.GetPrevSibling(titm).IsOk():
                    titm = self.list_events.GetPrevSibling(titm)
                else:
                    titm = self.list_events.GetItemParent(titm)
                if isinstance(self.list_events.GetItemPyData(titm), ScanEvent):
                    break
            ditm = titm
            ev = self.list_events.GetItemPyData(ditm) 
            
        if ev.is_loop or ev.is_root:
            # target item is a recipient item => dropped as child
            titm = self.list_events.GetLastChild(ditm)
            parent = ditm
        else:
            # item will be dropped before target
            titm = self.list_events.GetPrevSibling(ditm)
            while titm.IsOk():
                if isinstance(self.list_events.GetItemPyData(titm), ScanEvent):
                    break
                titm = self.list_events.GetPrevSibling(titm)
            parent = self.list_events.GetItemParent(ditm)
            if not(titm.IsOk()):
                # previous ScanEvent item is the parent item, must find where to place
                titm = self.list_events.GetFirstChild(parent)[0]
                if not(isinstance(self.list_events.GetItemPyData(titm),PropertyNode)):
                    # this ScanEvent instance doesn't have a property node
                    titm = parent
        # check that target is not a child of dropped item
        dev = self.list_events.GetItemPyData(parent)
        if stree.IsDataInTree(dev): return
        
        if stree.data.is_root:
            # if dropped item is root, placed before previous root item
            while titm.IsOk():
                ev = self.list_events.GetItemPyData(titm)
                if isinstance(ev, ScanEvent):
                    if ev.is_root:
                        break
                titm = self.list_events.GetItemParent(titm)
            titm = self.list_events.GetPrevSibling(titm)
            parent = self.list_events.GetRootItem()
            if not(titm.IsOk()):
                titm = parent

        if parent.IsOk():
            # move dropped item to the right place
            nitm = self.list_events.InsertItem(parent,titm,stree.text,stree.image)
            self.list_events.CreateItemSubTree(nitm, stree)
            self.list_events.Delete(oitm)
            self.list_events.SelectItem(nitm)

    def OnButtonUp(self, event = None):
        """
        
            Actions triggered by Up button press.
            
            Parameters:
                event    -    wx.Event
        
        """
        pos = self.list_events.Selection
        if isinstance(self.list_events.GetItemPyData(pos),ScanEvent):
            self.list_events.MoveItemUp(pos,ScanEvent)

    def OnButtonDown(self, event = None):
        """
        
            Actions triggered by Down button press.
            
            Parameters:
                event    -    wx.Event
        
        """
        pos = self.list_events.Selection
        if isinstance(self.list_events.GetItemPyData(pos),ScanEvent):
            self.list_events.MoveItemDown(pos,ScanEvent)

    def OnButtonRun(self, event = None):
        """
        
            Actions triggered by Run/Stop button press.
            
            Parameters:
                event    -    wx.Event
        
        """
        if self.scanThread == None:
            pos = self.list_events.GetSelection()
            ev = self.list_events.GetItemPyData(pos)
            while pos.IsOk():
                if hasattr(ev,'is_root'):
                    if ev.is_root:
                        break
                pos = self.list_events.GetItemParent(pos)
                ev = self.list_events.GetItemPyData(pos)
            if pos.IsOk():
                self.OnRunSequence(pos)
        else:
            pub.sendMessage("scan.stop")
    
    def OnStopMeasurement(self, inst = None):
        """
        
            Actions following stop measurement request.
            
            Parameters:
                event    -    wx.Event
        
        """
        while(self.scanThread.is_alive()):
            sleep(0.1)
        self.scanThread = None
        # set interface to idle (non-scanning) mode
        self.ToggleControls(True) # scan event list controls
    
    def ToggleControls(self, state=True):
        """
        
            Toggle state of widgets.
            
            Parameters:
                state    -    True = idle state, False = scan running
        
        """
        self.list_events.Enable(state)
        self.button_remove.Enable(state)
        self.button_down.Enable(state)
        self.button_add.Enable(state)
        self.button_up.Enable(state)
        self.button_run.Switch(state)

