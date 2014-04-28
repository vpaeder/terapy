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

    Functions and classes to handle input devices.
    
    Properties:
        modules    -    list of available device drivers

    Each device driver must be implemented as a InputDevice class (see base.py).
    InputDevice classes contained in Python scripts within this folder will be
    automatically recognized and added to input device driver list. 

"""

import os
from terapy.hardware.input.base import InputDevice
from terapy.core import check_py
from terapy.core import parse_modules

# import input device driver classes
curdir = os.path.dirname(__file__)
modules = parse_modules(__package__, curdir, InputDevice)

# search for custom modules
from terapy.core import module_path
if os.path.exists(module_path):
    modules.extend(parse_modules("custom.hardware.input.", module_path, InputDevice))
