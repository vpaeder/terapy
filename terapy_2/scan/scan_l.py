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
    List scan event class
"""

from terapy.scan.scan_s import Scan
import wx.grid
from wx.lib import sheet
from numpy import array, insert, delete, arange
from time import sleep
from terapy.core import icon_path

class Scan_L(Scan):
    """
        List scan event class
        
        Scan given axis device following given list of values.
    """
    __extname__ = "List scan"
    def __init__(self, parent = None):
        Scan.__init__(self, parent)
        self.axis = 0
        self.N = 1
        self.list = [0.0]
        self.propNames = ["Axis"]
        self.config = ["axis","list","N"]
    
    def refresh(self):
        Scan.refresh(self)
        self.N = len(self.list)
        
    def run(self, data):
        self.itmList = self.get_children()
        ax = self.axlist[self.axis]
        ax.prepareScan()
        # scan selected axis from min to max
        coords = array(self.list)
        n=-1
        while self.can_run and n<self.N-1:
            n+=1
            ax.goTo(coords[n])
            while (ax.get_motion_status() != 0 and self.can_run):
                sleep(0.01)
            data.SetCoordinateValue(self.m_ids, ax.pos()) # read axis position
            self.run_children(data)
            data.Increment(self.m_ids)
        data.Decrement(self.m_ids)
        data.DecrementScanDimension(self.m_ids)
        return True

    def set(self, parent=None):
        self.refresh()
        dlg = ListLoopSettingsDialog(parent, axlist=[x.name for x in self.axlist], axis=self.axis, dlist=self.list)
        if dlg.ShowModal() == wx.ID_OK:
            self.axis, self.list = dlg.GetValue()
            self.N = len(self.list)
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def populate(self):
        try:
            self.propNodes = [self.axlist[self.axis].name]
        except:
            self.propNodes = [""]
        self.create_property_root()
        self.set_property_nodes(True)

    def set_property(self, pos, val):
        try:
            if pos==0:
                self.axis = int(val)
        except:
            pass
        self.propNodes = [self.axlist[self.axis].name]
        self.set_property_nodes()
        
class ListLoopSettingsDialog(wx.Dialog):
    """
    
        List scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Loop properties", axlist=[], axis = 0, dlist=[0.0]):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                axlist    -    list of axis devices (list of str)
                axis      -    default selection (int)
                dlist     -    default list (list of float)
        
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.label_axis = wx.StaticText(self, -1, "Axis")
        self.choice_axis = wx.Choice(self, -1, choices=axlist)
        self.sheet = sheet.CSheet(self)
        self.button_add = wx.BitmapButton(self, -1, wx.Image(icon_path + "list-add.png").ConvertToBitmap())
        self.button_remove = wx.BitmapButton(self, -1, wx.Image(icon_path + "list-remove.png").ConvertToBitmap())
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.button_add, 0, wx.EXPAND|wx.ALL, 2)
        hbox2.Add(self.button_remove, 0, wx.EXPAND|wx.ALL, 2)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.sheet, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox2, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.choice_axis.SetSelection(axis)

        self.sheet.SetSelectionMode(1)
        self.table = PointList("Measurement points",dlist)
        self.sheet.SetTable(self.table)
        self.sheet.selected = []
        self.sheet.SetMaxSize((-1,200))
        self.sheet.SetMinSize((-1,200))
        self.sheet.AutoSizeColumn(0)

        self.Fit()
                
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnSelectSheetCell, self.sheet)
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnSelectSheetRange, self.sheet)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.button_add)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.button_remove)
    
    def OnSelectSheetCell(self, event):
        """
        
            Actions triggered by cell selection in list.
            
            Parameters:
                event    -    wx.Event
        
        """
        if event.Selecting():
            self.sheet.SelectedCells.append(event.GetRow())
            self.sheet.selected = [event.GetRow()]
        event.Skip()

    def OnSelectSheetRange(self, event):
        """
        
            Actions triggered by cell range selection in list.
            
            Parameters:
                event    -    wx.Event
        
        """
        if event.Selecting():
            self.sheet.selected = range(event.GetTopRow(),event.GetBottomRow()+1,1)
        event.Skip()

    def OnSheetCopy(self, event = None):
        """
        
            Actions triggered by copy action on list.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.sheet.Copy()

    def OnSheetPaste(self, event = None):
        """
        
            Actions triggered by paste action on list.
            
            Parameters:
                event    -    wx.Event
        
        """
        if not wx.TheClipboard.IsOpened():
            # get data from clipboard
            wx.TheClipboard.Open()
            do = wx.TextDataObject()
            wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            values = do.GetText().split()
            
            # find where to paste and adapt the array if necessary 
            if self.sheet.NumberRows<len(values):
                self.table._data = arange(0.0,len(values),1.0).reshape(len(values),1)
            for nv in range(0,len(values)):
                self.table._data[nv][0] = float(values[nv])
            self.sheet.SetTable(self.table)

    def OnAdd(self, event = None):
        """
        
            Actions triggered when Add button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.table.InsertRows(self.sheet.selected,1)
        self.sheet.ProcessTableMessage(wx.grid.GridTableMessage(self.table,wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,1))
        self.sheet.ForceRefresh()
    
    def OnRemove(self, event = None):
        """
        
            Actions triggered when Remove button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        for x in self.sheet.selected:
            self.sheet.DeselectRow(x)
        self.table.DeleteRows(self.sheet.selected,0)
        self.sheet.ProcessTableMessage(wx.grid.GridTableMessage(self.table,wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,0,len(self.sheet.selected)))
        self.sheet.ForceRefresh()
        self.sheet.selected = []
        
    def GetValue(self):
        """
        
            Return dialog values.
            
            Output:
                index of selected axis device (int), list of points (float)
        
        """
        return self.choice_axis.GetSelection(), self.table._data.reshape(len(self.table._data))

class PointList(wx.grid.PyGridTableBase):
    """
    
        Table base class for point list
    
    """
    def __init__(self,title="",data=[0.0]):
        """
        
            Initialization.
            
            Parameters:
                title    -    column titles (list of str)
                data     -    list of points (list of float)
        
        """
        wx.grid.PyGridTableBase.__init__(self)
        self._cols = [title]
        self._data = array(data)
        self._data = self._data.reshape(len(self._data),1)

    def GetColLabelValue(self, col):
        """
        
            Return column label for given index.
            
            Parameters:
                col    -    column index (int)
            
            Output:
                column label (str)
        
        """
        return self._cols[col]

    def GetNumberRows(self):
        """
        
            Return number of rows.
            
            Output:
                number of rows (int)
        
        """
        return len(self._data)

    def GetNumberCols(self):
        """
        
            Return number of columns.
            
            Output:
                number of columns (int)
        
        """
        return len(self._cols)

    def GetValue(self, row, col):
        """
        
            Return value for given row and column index.
            
            Parameters:
                row    -    row index (int)
                col    -    column index (int)
            
            Output:
                value (float)
        
        """
        try:
            return str(self._data[row,col])
        except:
            return 0

    def SetValue(self, row, col, val):
        """
        
            Set value of given row and column index.
            
            Parameters:
                row    -    row index (int)
                col    -    column index (int)
                value  -    value (float)
        
        """
        try:
            self._data[row,col] = float(val)
        except:
            pass
    
    def InsertRows(self, pos, num):
        """
        
            Insert given number of empty rows at given position.
            
            Parameters:
                pos    -    position (int)
                num    -    number of new rows (int)
        
        """
        if len(pos)>0:
            self._data = insert(self._data,pos,0.0)
            self._data = self._data.reshape(len(self._data),1)
        else:
            self._data = insert(self._data,0,0.0)
            self._data = self._data.reshape(len(self._data),1)
        return True
    
    def DeleteRows(self, pos, num=0):
        """
        
            Delete given row.
            
            Parameters:
                pos    -    position (int)
                num    -    not used, only here to satisfy class specs
            
            Output:
                True if successful
        
        """
        if len(pos)>0:
            self._data = delete(self._data,pos)
            self._data = self._data.reshape(len(self._data),1)
            return True
        else:
            return False
