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

    Functions and classes to handle plot canvases and plots.
    
    Properties:
        canvas_modules    -    list of available canvas classes
        plot_modules      -    list of available plot classes

    Each canvas must be implemented as a PlotCanvas class (see base.py).
    Each plot must be implemented as a Plot class (see base.py).
    PlotCanvas/Plot classes contained in Python scripts within this folder will be
    automatically recognized and added to appropriate list.
 
"""

from base import PlotCanvas, Plot
from terapy.core import check_py, parse_modules, module_path
import os

# import canvas and plot classes
curdir = os.path.dirname(__file__)
plot_modules = []
canvas_modules = []
plot_modules = parse_modules(__package__, curdir, Plot)
canvas_modules = parse_modules(__package__, curdir, PlotCanvas)

# search for custom modules
if os.path.exists(module_path):
    plot_modules.extend(parse_modules("custom.plot.", module_path, Plot))
    canvas_modules.extend(parse_modules("custom.canvas.", module_path, PlotCanvas))
