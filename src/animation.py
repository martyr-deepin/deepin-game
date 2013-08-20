#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011~2013 Deepin, Inc.
#               2011~2013 Kaisheng Ye
#
# Author:     Kaisheng Ye <kaisheng.ye@gmail.com>
# Maintainer: Kaisheng Ye <kaisheng.ye@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from icon_window import IconWindow
from deepin_utils.math_lib import solve_parabola
from dtk.ui.timeline import Timeline, CURVE_SINE
import utils

def favorite_animation(window):

    # Add install animation.
    (screen, px, py, modifier_type) = window.get_display().get_pointer()
    ax, ay = px, py
    
    (wx, wy) = window.window.get_origin()
    offset_bx = 480
    offset_by = 5
    bx, by = wx + offset_bx, wy + offset_by
    
    offset_cx = 10
    offset_cy = 10
    if ax < bx:
        cx, cy = wx + offset_bx + offset_cx, wy + offset_by + offset_cy
    else:
        cx, cy = wx + offset_bx - offset_cx, wy + offset_by + offset_cy
    
    [[a], [b], [c]] = solve_parabola((ax, ay), (bx, by), (cx, cy))
    
    icon_window = IconWindow(utils.get_common_image('heart/heart_on.png'))
    icon_window.move(ax, ay)
    icon_window.show_all()
    
    timeline = Timeline(500, CURVE_SINE)
    timeline.connect("update", lambda source, status: update(source, status, icon_window, (ax, ay), (bx, by), (cx, cy), (a, b, c)))
    timeline.connect("completed", lambda source: finish(source, icon_window))
    timeline.run()

def update(source, status, icon_window, (ax, ay), (bx, by), (cx, cy), (a, b, c)):
    move_x = ax + (cx - ax) * status
    move_y = a * pow(move_x, 2) + b * move_x + c
    
    icon_window.move(int(move_x), int(move_y))
    icon_window.show_all()
      
def finish(source, icon_window):
    icon_window.destroy()
