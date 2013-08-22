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

from dtk.ui.init_skin import init_skin
from deepin_utils.file import get_parent_dir
from constant import PROGRAM_VERSION, PROGRAM_NAME
from dtk.ui.theme import DynamicPixbuf, DynamicColor
import os

app_theme = init_skin(
        PROGRAM_NAME, 
        PROGRAM_VERSION,
        "green_yellow",
        os.path.join(get_parent_dir(__file__, 2), "skin"),
        os.path.join(get_parent_dir(__file__, 2), "app_theme"),
    )

def app_theme_get_dynamic_pixbuf(filename):
    '''
    from file get dynamic pixbuf
    @param filename: the image filename
    @return: a DynamicPixbuf
    '''
    return DynamicPixbuf(app_theme.get_theme_file_path(filename))

def app_theme_get_dynamic_color(color):
    '''
    get them color
    @param color: a hex color string
    @return: a DynamicColor
    '''
    return DynamicColor(color)

