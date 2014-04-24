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

    Functions for menu handling

"""

def GetItemIds(menu):
    """
    
        Return list of menu item ids for given menu
        
        Parameters:
            menu    -    menu (wx.Menu)
        
        Output:
            menu item ids (list)
    
    """
    mitems = menu.GetMenuItems()
    mids = []
    for x in mitems:
        mids.append(x.Id)
    return mids
