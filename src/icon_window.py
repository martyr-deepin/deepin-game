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

import gtk
import gobject
import cairo
from dtk.ui.draw import draw_pixbuf

class IconWindow(gtk.Window):
    def __init__(self, icon_path):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap())
        self.set_decorated(False)
        self.icon_pixbuf = gtk.gdk.pixbuf_new_from_file(icon_path)
        self.window_width = self.icon_pixbuf.get_width()
        self.window_height = self.icon_pixbuf.get_height()
        self.set_geometry_hints(
            None,
            self.window_width,
            self.window_height,
            self.window_width,
            self.window_height,
            -1, -1, -1, -1, -1, -1)
        
        self.connect("expose-event", self.expose_icon_window)
        
    def expose_icon_window(self, widget, event):
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation

        # Clear color to transparent window.
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
                
        draw_pixbuf(
            cr,
            self.icon_pixbuf,
            rect.x,
            rect.y)
        
        return True

gobject.type_register(IconWindow)
