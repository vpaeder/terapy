#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Vincent Paeder
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

    Move axis device until some condition is reached

"""

from terapy.scan.base import ScanEvent
import wx
from time import sleep
from terapy.core.choice import ChoicePopup
from terapy.core import icon_path

class MoveUntil(ScanEvent):
    """
    
        Move axis device scan event class
        
        Move selected axis device until some condition is reached.
    
    """
    __extname__ = "Move Until"
    def __init__(self, parent = None):
        ScanEvent.__init__(self, parent)
        self.axis = 0
        self.axlist = []
        self.trlist = []
        self.step = 0.0
        self.delay = 0.1
        self.trigger = 0
        self.quantity = 0
        self.condition = 0
        self.condlist = ["Equal","Smaller than","Greater than","Increased by","Decreased by","Multiplied by","Divided by"]
        self.value = 1.0
        self.propNames = ["Axis","Step size","Delay","Trigger", "Quantity","Condition","Value"]
        self.config = ["axis","step","delay","trigger","quantity","condition","value"]
        self.is_axis = True
    
    def refresh(self):
        ScanEvent.refresh(self)
        from terapy.hardware import devices
        self.axlist = devices['axis']
        self.trlist = devices['input']
        if self.axis>=len(self.axlist): self.axis = len(self.axlist)-1
        if self.axis<0: self.axis = 0
        if self.trigger>=len(self.trlist): self.trigger = len(self.trlist)-1
        if self.trigger<0: self.trigger = 0
        if self.quantity>=len(self.trlist[self.trigger].qtynames):
            self.quantity = len(self.trlist[self.trigger].qtynames)-1

    def run(self, data):
        if self.can_run:
            ax = self.axlist[self.axis]
            tr = self.trlist[self.trigger]
            v0 = tr.read()[self.quantity]
            cond = True
            
            while cond and self.can_run:
                v = tr.read()[self.quantity]
                if self.condition==0: # trigger is equal to
                    cond = (v!=self.value)
                elif self.condition==1: # trigger is smaller than
                    cond = (v>=self.value)
                elif self.condition==2: # trigger is larger than
                    cond = (v<=self.value)
                elif self.condition==3: # trigger increased by
                    cond (v>=(v0+self.value))
                elif self.condition==4: # trigger decreased by
                    cond (v<=(v0-self.value))
                elif self.condition==5: # trigger multiplied by
                    cond (v>=v0*self.value)
                elif self.condition==6: # trigger divided by
                    cond (v<=v0/self.value)
                
                if not(cond): break
                
                # condition is not met => move axis
                p0 = ax.pos()
                ax.goTo(p0+self.step)
                # wait that movement is complete
                while (ax.get_motion_status() != 0 and self.can_run):
                    sleep(0.01)
                # wait for specified additional delay
                t0 = 0.0
                while (t0<self.delay and self.can_run):
                    sleep(0.01)
                    t0+=0.01
                    
        
    def set(self, parent=None):
        self.refresh()
        dlg = MoveUntilSelectionDialog(parent, axlist=[x.name for x in self.axlist], axis=self.axis, step=self.step, delay=self.delay, trlist=self.trlist, trigger=self.trigger, quantity=self.quantity, condlist=self.condlist, condition=self.condition, value=self.value)
        if dlg.ShowModal() == wx.ID_OK:
            self.axis, self.step, self.delay, self.trigger, self.quantity, self.condition, self.value = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def populate(self):
        self.propNodes = [self.axlist[self.axis].name, self.step, self.delay, self.trlist[self.trigger].name, self.trlist[self.trigger].qtynames[self.quantity], self.condlist[self.condition], self.value]
        self.create_property_root()
        self.set_property_nodes(True)

    def set_property(self, pos, val):
        try:
            if pos==0:
                self.axis = int(val)
            elif pos==1:
                self.step = float(val)
            elif pos==2:
                self.delay = float(val)
            elif pos==3:
                self.trigger = int(val)
            elif pos==4:
                self.quantity = int(val)
            elif pos==5:
                self.condition = int(val)
            elif pos==6:
                self.value = float(val)
        except:
            pass
        self.propNodes = [self.axlist[self.axis].name, self.step, self.delay, self.trlist[self.trigger].name, self.trlist[self.trigger].qtynames[self.quantity], self.condlist[self.condition], self.value]
        self.set_property_nodes(True)
        
    def edit_label(self, event, pos):
        if pos==0:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(0))
            w = ChoicePopup(self.host,-1,choices=[x.name for x in self.axlist],pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.axis)
            w.Bind(wx.EVT_CHOICE,self.onSelectAxis)
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectAxis)
            #else:
            #    w.Bind(wx.EVT_LEAVE_WINDOW,self.onSelectAxis)
            self.set_property_nodes(True)
        elif pos==3:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(3))
            w = ChoicePopup(self.host,-1,choices=[x.name for x in self.trlist],pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.trigger)
            w.Bind(wx.EVT_CHOICE,self.onSelectTrigger)
            w.SetFocus()
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectTrigger)
        elif pos==4:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(4))
            w = ChoicePopup(self.host,-1,choices=self.trlist[self.trigger].qtynames,pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.quantity)
            w.Bind(wx.EVT_CHOICE,self.onSelectQuantity)
            w.SetFocus()
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectQuantity)
        elif pos==5:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(5))
            w = ChoicePopup(self.host,-1,choices=self.condlist,pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.condition)
            w.Bind(wx.EVT_CHOICE,self.onSelectCondition)
            w.SetFocus()
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectCondition)
            

    def onSelectAxis(self, event=None):
        self.axis = event.GetEventObject().GetSelection()
        self.propNodes[0] = self.axlist[self.axis].name
        self.set_property_nodes(True)
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)

    def onSelectTrigger(self, event=None):
        self.trigger = event.GetEventObject().GetSelection()
        self.propNodes[3] = self.trlist[self.trigger].name
        self.refresh()
        self.propNodes[4] = self.trlist[self.trigger].qtynames[self.quantity]
        self.set_property_nodes()
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)

    def onSelectQuantity(self, event=None):
        self.quantity = event.GetEventObject().GetSelection()
        self.propNodes[4] = self.trlist[self.trigger].qtynames[self.quantity]
        self.set_property_nodes()
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)

    def onSelectCondition(self, event=None):
        self.condition = event.GetEventObject().GetSelection()
        self.propNodes[5] = self.condlist[self.condition]
        self.set_property_nodes()
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)
    
    def get_icon(self):
        return wx.Image(icon_path + "event-move.png").ConvertToBitmap()

class MoveUntilSelectionDialog(wx.Dialog):
    """
    
        Move axis device scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Move axis device until", axlist = [], axis = 0, step=0.1, delay=0.1, trlist=[], trigger=0, quantity=0, condlist=[], condition=0, value=0.1):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                axlist    -    list of axis devices (list of str)
                axis      -    default selection (int)
                position  -    position (float)
                relative  -    if True, move is relative, absolute if False
        
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.label_axis = wx.StaticText(self, -1, "Axis")
        self.choice_axis = wx.Choice(self, -1, choices=axlist)
        self.label_step = wx.StaticText(self, -1, "Step size (axis units)")
        self.input_step = wx.TextCtrl(self, -1, str(step))
        self.label_delay = wx.StaticText(self, -1, "Delay between steps (s)")
        self.input_delay = wx.TextCtrl(self, -1, str(delay))
        self.label_trigger = wx.StaticText(self, -1, "Trigger device")
        self.choice_trigger = wx.Choice(self, -1, choices=[x.name for x in trlist])
        self.label_quantity = wx.StaticText(self, -1, "Trigger quantity")
        self.choice_quantity = wx.Choice(self, -1, choices=trlist[trigger].qtynames)
        self.label_condition = wx.StaticText(self, -1, "Condition")
        self.choice_condition = wx.Choice(self, -1, choices=condlist)
        self.label_value = wx.StaticText(self, -1, "Value")
        self.input_value = wx.TextCtrl(self, -1, str(value))
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        self.choice_axis.SetSelection(axis)
        self.choice_trigger.SetSelection(trigger)
        self.choice_quantity.SetSelection(quantity)
        self.choice_condition.SetSelection(condition)
        self.Bind(wx.EVT_CHOICE, self.OnTriggerSelect, self.choice_trigger)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_step, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_step, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_delay, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_delay, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_trigger, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_trigger, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_quantity, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_quantity, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_condition, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_condition, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_value, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_value, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        
        self.trlist = trlist
    
    def OnTriggerSelect(self, event=None):
        """
        
            Callback for trigger selection.
            
            Parameters:
                event    -    wx.Event
        
        """
        trigger = self.choice_trigger.GetSelection()
        quantity = self.choice_quantity.GetSelection()
        self.choice_quantity.Clear()
        self.choice_quantity.AppendItems(self.trlist[trigger].qtynames)
        if quantity>=len(self.trlist[trigger].qtynames): quantity = len(self.trlist[trigger].qtynames)-1 
        self.choice_quantity.SetSelection(quantity)
    
    def GetValue(self):
        """
        
            Return dialog values.
            
            Output:
                selected axis device index (int), position (float), absolute/relative move (bool)
        
        """
        return self.choice_axis.GetSelection(), float(self.input_step.GetValue()), float(self.input_delay.GetValue()), self.choice_trigger.GetSelection(), self.choice_quantity.GetSelection(), self.choice_condition.GetSelection(), float(self.input_value.GetValue())
