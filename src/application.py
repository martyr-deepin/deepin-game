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
from dtk.ui.application import Application
from dtk.ui.constant import DEFAULT_FONT_SIZE
from titlebar import Titlebar

class PlayerApplication(Application):
    def __init__(self, 
                 app_support_colormap=True, 
                 resizable=True,
                 window_type=gtk.WINDOW_TOPLEVEL,
                 destroy_func=None,
                 always_at_center=True,
                 max_callback=None,
                 ):
        '''
        Initialize the Application class.
        
        @param app_support_colormap: Set False if your program don't allow manipulate colormap, 
        such as mplayer, otherwise you should keep this option as True.
        @param resizable: Set this option with False if you want window's size fixed, default is True.
        '''
        # Init.
        Application.__init__(
                self,
                app_support_colormap,
                resizable,
                window_type,
                destroy_func,
                always_at_center
                )

        ''' Initialize 
        self.app_support_colormap = app_support_colormap
        self.resizable = resizable
        self.window_type = window_type
        self.close_callback = self.close_window
        self.skin_preview_pixbuf = None
        self.destroy_func = destroy_func
        self.always_at_center = always_at_center

        self.init()
        '''

        if max_callback:
            self.max_callback = max_callback
        else:
            self.max_callback = lambda w:self.window.toggle_max_window()

        self.skin_preview_pixbuf = None

    def add_titlebar(self,
                     button_mask=["theme", "menu", 'min',"max", "close"],
                     icon_path=None, 
                     app_name=None, 
                     title=None, 
                     add_separator=False, 
                     show_title=True, 
                     enable_gaussian=True, 
                     name_size=DEFAULT_FONT_SIZE,
                     title_size=DEFAULT_FONT_SIZE,
                     ):
        '''
        Add titlebar to the application.
        
        Connect click signal of the standard button to default callback.
        
        @param button_mask: A list of string, each of which stands for a standard button on top right of the window. By default, it's ["theme", "menu", "max", "min", "close"].
        @param icon_path: The path of icon image.
        @param app_name: The name string of the application, which will be displayed just next to the icon_dpixbuf. By default, it is None.
        @param title: The title string of the window, which will be displayed on the center of the titlebar. By default, it is None.
        @param add_separator: If True, add a line between the titlebar and the body of the window. By default, it's False.
        @param show_title: If False, the titlebar will not be displayed. By default, it's True.
        @param enable_gaussian: Set it as False if don't want gaussian application title. By default, it's True.
        @param name_size: The size of name, default is DEFAULT_FONT_SIZE.
        @param title_size: The size of title, default is DEFAULT_FONT_SIZE.
        '''
        # Init titlebar.
        self.titlebar = Titlebar(button_mask, 
                                 icon_path, 
                                 app_name, 
                                 title, 
                                 add_separator, 
                                 show_title=show_title, 
                                 enable_gaussian=enable_gaussian,
                                 name_size=name_size,
                                 title_size=title_size,
                                 )
        if "theme" in button_mask:
            self.titlebar.theme_button.connect("clicked", self.theme_callback)
        if "menu" in button_mask:
            self.titlebar.menu_button.connect("clicked", self.menu_callback)
        if "min" in button_mask:
            self.titlebar.min_button.connect("clicked", lambda w: self.window.min_window())
        if "max" in button_mask:
            self.titlebar.max_button.connect("clicked", self.max_callback)
        if "close" in button_mask:
            self.titlebar.close_button.connect("clicked", self.close_callback)
        if self.resizable:
            self.window.add_toggle_event(self.titlebar)
        self.window.add_move_event(self.titlebar)

        # Show titlebar.
        self.show_titlebar()
        
        if app_name != None:
            self.window.set_title(app_name)
