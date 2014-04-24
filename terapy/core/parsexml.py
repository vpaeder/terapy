#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013  Vincent Paeder
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

    Functions for XML configuration file parsing

"""

def ParseAttributes(attrs,recipient):
    """
    
        Convert XML attributes into object variables
        
        Parameters:
            attrs        -    XML attributes (xmldom key)
            recipient    -    class with appropriate class variables
    
    """
    # read attributes from a xml node, convert to appropriate type
    for y in attrs.keys(): # set attributes
        if hasattr(recipient,y):
            t = type(getattr(recipient,y)) # convert read value to correct type
            if hasattr(t,'__iter__'): # list, must be processed specially
                v = getattr(recipient,y)
                if len(v)>0:
                    t2 = type(v[0])
                else:
                    t2 = float
                v = attrs[y].value
                if v.count(",")>0:
                    v = v.replace("[","").replace("]","").split(",")
                else:
                    v = v.replace("[","").replace("]","").split("  ")
                setattr(recipient,y,t(map(t2,v)))
            else:
                setattr(recipient,y,t(attrs[y].value))
