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

    Miscellaneous classes and functions implementing several core (and not so core) functionalities of TeraPy.

"""

import os
from xml.dom import minidom
import plotpanel

# get root path
root_path = os.path.dirname(os.path.abspath( __file__ ))
# normcase transforms "/" into "\" under Windows
root_path = root_path.split(os.path.normcase("/"))
root_path[-1] = ""
root_path = os.path.normcase("/".join(root_path)) # directory where main file is
icon_path = os.path.normcase(root_path + "icons/") # where icons are stored

default_units = {'time':'ps','frequency':'THz','length':'um','voltage':'V','current':'A'} # dictionnary of default units

# search for main config file (paths + extra stuff)
inipath = []
# first in user directory
inipath.append(os.path.expanduser("~") + os.path.normcase("/") + "terapy.ini")
# then in current directory
inipath.append(os.path.abspath(os.curdir) + os.path.normcase("/") + "terapy.ini")
# then in current/config directory
inipath.append(os.path.abspath(os.curdir) + os.path.normcase("/config/") + "terapy.ini")

candidates = []
for x in inipath:
    if os.path.exists(x):
        candidates.append(x)

main_config_file = None
for cnd in candidates:
    try:
        xmldoc = minidom.parse(cnd).getElementsByTagName('config')
        for x in xmldoc:
            scope = x.attributes['scope'].value
            if scope == 'terapy':
                for y in x.childNodes:
                    if y.nodeName == 'default_path':
                        default_path = y.attributes['value'].value
                    elif y.nodeName == 'user_path':
                        user_path = y.attributes['value'].value
                    elif y.nodeName == 'config_path':
                        config_path = y.attributes['value'].value
                    elif y.nodeName == 'filter_path':
                        filter_path = y.attributes['value'].value
                    elif y.nodeName == 'module_path':
                        module_path = y.attributes['value'].value
                    elif y.nodeName == 'refresh_delay':
                        refresh_delay = float(y.attributes['value'].value)
                    elif y.nodeName == 'units':
                        default_units[str(y.attributes['type'].value)] = str(y.attributes['symbol'].value) 
        main_config_file = cnd
        break # stop after 1st valid file
    except:
        pass
 
app_path = os.path.abspath(os.curdir) + os.path.normcase("/")
if not('default_path' in locals()):
    default_path = app_path + "backup" # this is where to save the backups
if not('user_path' in locals()):
    user_path = app_path + "data"      # this is where the user can save additionally
if not('config_path' in locals()):
    config_path = app_path + "config"  # where the configuration files are stored
if not('filter_path' in locals()):
    filter_path = app_path + "filters"  # where the configuration files are stored
if not('module_path' in locals()):
    module_path = app_path + "modules"  # where custom modules may be stored
if not('refresh_delay' in locals()):
    refresh_delay = 0.2                 # delay (in seconds) after which the display will be updated during scan 

# test if folders exist
for x in ['default_path', 'user_path', 'config_path', 'filter_path', 'module_path']:
    if not(os.path.exists(locals()[x])):
        print "WARNING: %s = %s is invalid. Setting to %s" % (x, locals()[x], app_path)
        locals()[x] = app_path

# search for config files in config directory
# assume .ini extension
configfiles = os.listdir(config_path)
device_file = None
filter_file = None
event_file = None
for fname in configfiles:
    fext = fname.split(".")[-1].lower()
    if fext=="ini":
        fullname = config_path + os.path.normcase("/") + fname
        xmldoc = minidom.parse(fullname).getElementsByTagName('config') 
        for x in xmldoc:
            scope = x.attributes['scope'].value
            if scope == 'devices' and device_file==None:
                device_file = fullname
                break
            elif scope == 'filters' and filter_file==None:
                filter_file = fullname
                break
            elif scope == 'events' and event_file==None:
                event_file = fullname
                break

def check_py(fname):
    """
    
        Check that the given file name is a python script, compiled or not.
        
        Parameters:
            fname    -    file name (str)
        
        Output:
            True/False
    
    """
    (name,ext) = os.path.splitext(fname)
    if [".py",".pyc",".pyd"].count(ext)>0 and name!="__init__":
        return True
    else:
        return False

def parse_modules(package, dirname, cls):
    """
    
        Parse for modules of given class in given directory.
        
        Parameters:
            package    -    package prefix (str)
            dirname    -    directory name (str)
            cls        -    class type
        
        Output:
            module list (list of type cls)
    
    """
    import imp
    imports = [fname for fname in os.listdir(dirname) if check_py(fname)]
    modules = []
    modnames = []
    for mod_name in imports:
        try:
            if mod_name.endswith('pyc'):
                mod = imp.load_compiled(os.path.splitext(mod_name)[0], dirname + os.path.normcase("/") + mod_name)
            elif mod_name.endswith('py'):
                mod = imp.load_source(os.path.splitext(mod_name)[0], dirname + os.path.normcase("/") + mod_name)
            elif mod_name.endswith('pyd'):
                mod = imp.load_dynamic(os.path.splitext(mod_name)[0], dirname + os.path.normcase("/") + mod_name)
        except:
            print "WARNING: can't import module " + package + "." + mod_name
            mod = None
        
        if mod!=None:
            for attr in mod.__dict__:
                if not attr.startswith('_'):
                    pa = getattr(mod, attr)
                    try:
                        if issubclass(pa,cls) and pa!=cls and  modnames.count(pa.__name__)==0:
                            modules.append(pa)
                            modnames = [x.__name__ for x in modules]
                    except:
                        pass
    return modules
