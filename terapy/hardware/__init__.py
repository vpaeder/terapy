#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2013 Daniel Dietze, 2013-2014  Vincent Paeder
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

    Functions and classes to handle hardware devices.
    
    Global variables:
        devices    -    list of loaded devices

"""

# list of all devices
devices = {'input':[],'axis':[]}

# imports
# operating system
import os
import sys
# device descriptions
from terapy.hardware import input
from terapy.hardware import axes

def initiate_hardware():
    """
    
        Initialize loaded hardware devices.
    
    """
    global devices # use global device list
    print "init input devices"
    for dev in devices["input"]:
        try:
            dev.initialize()
        except:
            print "ERROR:", dev.ID, "is not responding! Rescan of hardware might solve the problem.."
    print "init axis devices"
    for dev in devices["axis"]:
        try:
            dev.initialize()
        except:
            print "ERROR:", dev.ID, "is not responding! Rescan of hardware might solve the problem.."
    

def get_hardware_info(doc, root, with_val=False):
    """
    
        Store informations on loaded devices in given XML document.
        
        Parameters:
            doc         -    minidom XML document
            root        -    root XML element under which to store
            with_val    -    if True, store snapshot of hardware state
    
    """
    for x in devices["input"]:
        p = doc.createElement("input")
        p.attributes["handle"] = x.address
        p.attributes["driver"] = x.ID
        p.attributes["name"] = x.name
        root.appendChild(p)
        for y in x.config:
            a = doc.createElement("property")
            a.attributes[y] = str(getattr(x,y))
            p.appendChild(a)
        if with_val:
            # store current value
            a = doc.createElement("snapshot")
            p.appendChild(a)
            for y in x.state():
                b = doc.createElement("value")
                b.attributes["name"] = str(y[0])
                b.attributes["value"] = str(y[1])
                b.attributes["units"] = str(y[2])
                a.appendChild(b)
    
    for x in devices["axis"]:
        p = doc.createElement("axis")
        p.attributes["handle"] = x.address
        p.attributes["driver"] = x.ID
        p.attributes["name"] = x.name
        p.attributes["axis"] = str(x.axis)
        root.appendChild(p)
        for y in x.config:
            a = doc.createElement("property")
            a.attributes[y] = str(getattr(x,y))
            p.appendChild(a)
        if with_val:
            # store current value
            a = doc.createElement("snapshot")
            p.appendChild(a)
            for y in x.state():
                b = doc.createElement("value")
                b.attributes["name"] = str(y[0])
                b.attributes["value"] = str(y[1])
                b.attributes["units"] = str(y[2])
                a.appendChild(b)
    
def store_hardware_info():
    """
    
        Store configuration of loaded hardware devices in hardware configuration file.
    
    """
    global devices # use global device list
    from terapy.core import device_file
    
    if device_file==None:
        print "WARNING: device file not defined, saving to devices.ini"
        device_file = "devices.ini"
    path = os.path.join(os.path.dirname(sys.argv[0]), device_file)
    from xml.dom import minidom
    doc = minidom.Document()
    root = doc.createElement("config")
    root.attributes["scope"] = "devices"
    doc.appendChild(root)
    
    get_hardware_info(doc, root)
        
    f = open(path,'w')
    doc.writexml(f,indent="  ", addindent="  ", newl="\n")
    f.close()
    
    
def restore_hardware_info():
    """
    
        Load configuration of loaded hardware devices from hardware configuration file.
    
    """    
    global devices                         # use global device list
    create_default_devices()            # add default devices - this also initializes the devices dict properly
    from terapy.core import device_file
    if device_file==None:
        print "WARNING: no device_file defined"
        return # no file defined
    path = os.path.join(os.path.dirname(sys.argv[0]), device_file)
    from xml.dom import minidom
    x_input = minidom.parse(path).getElementsByTagName('input')
    x_axis = minidom.parse(path).getElementsByTagName('axis')
        
    for x in x_input:
        for y in input.modules:
            if x.attributes['driver'].value == y.__name__:
                try:
                    dev = y()
                    dev.assign(x.attributes['handle'].value, x.attributes['driver'].value, x.attributes['name'].value)
                    if x.hasChildNodes():
                        dev.xml2config(x.childNodes)
                    dev.initialize()
                    devices["input"].append(dev)
                except:
                    print "WARNING: Unable to create "+y.__name__+" device!"

    for x in x_axis:
        for y in axes.modules:
            if x.attributes['driver'].value == y.__name__:
                try:
                    dev = y()
                    dev.assign(x.attributes['handle'].value, x.attributes['driver'].value, x.attributes['name'].value, x.attributes['axis'].value)
                    if x.hasChildNodes():
                        dev.xml2config(x.childNodes)
                    dev.initialize()
                    devices["axis"].append(dev)
                except:
                    print "WARNING: Unable to create "+y.__name__+" device!"
    
    #initiate_hardware()

def create_default_devices():
    """
    
        Create default devices.
    
    """
    global devices
    devices = {"input":[],"axis":[]}
    dev = input.InputDevice()
    dev.assign("RANDOM", "RANDOM", "Random Numbers")
    devices["input"].append(dev)
    dev = axes.AxisDevice()
    dev.assign("TIME", "TIME", "Continuous Run", 1)
    devices["axis"].append(dev)
    
def scan_hardware():
    """
    
        Search for devices that can be handled by available modules.
     
    """
    global devices # use global device list
    # delete old device list
    create_default_devices()

    for x in input.modules:
        print "Probing for " + x.__name__ + "..."
        instr = x().detect()
        for y in instr:
            print "Found " + x.__name__ + " at address " + y[0]
            devices["input"].append(x())
            devices["input"][-1].assign(y[0], x.__name__, y[1])
    
    for x in axes.modules:
        print "Probing for " + x.__name__ + "..."
        instr = x().detect()
        for y in instr: 
            print y
            print "Found " + x.__name__ + " at address " + y[0] + ", axis " + str(y[2])
            devices["axis"].append(x())
            devices["axis"][-1].assign(y[0], x.__name__, y[1], y[2])

def get_widgets(parent=None):
    """
    
        Return list of widgets for loaded devices.
        
        Output:
            list of wx.Frame widgets
    
    """
    wlist = []
    for x in [x for y in (devices['input'],devices['axis']) for x in y]:
        w = x.widget(parent)
        if w!=None:
            for wi in w:
                wlist.append(wi)
    return wlist

def get_system_state():
    """
    
        Create XML tree containing state of loaded instruments.
        
        Output:
            minidom XML document
    
    """
    from xml.dom import minidom
    doc = minidom.Document()
    root = doc.createElement("systemState")
    doc.appendChild(root)
    get_hardware_info(doc, root, with_val=True)
    return doc

# if called as executable, display list of devices on screen
if __name__ == '__main__':
    print "scanning..."
    scan_hardware()
    print "found:"
    print "input devices:"
    for dev in devices['input']:
        print "\t", dev.address, ":", dev.name
    print "motion controllers:"
    for dev in devices['axis']:
        print "\t", dev.address, ":", dev.name
