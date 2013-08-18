#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
#             Kaisheng Ye <kaisheng.ye@gmail.com>
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

from dtk.ui.box import EventBox
from dtk.ui.button import ThemeButton, MenuButton, MinButton, MaxButton, CloseButton
from dtk.ui.draw import draw_line
from dtk.ui.label import Label
from dtk.ui.locales import _
from dtk.ui.constant import DEFAULT_FONT_SIZE
import dtk.ui.tooltip as Tooltip
from dtk.ui.utils import window_is_max
import gobject
import gtk
import pango

from theme import app_theme
from button import ToggleButton

def create_revert_button():    
    button = ToggleButton(
        app_theme.get_pixbuf("mode/simple_normal.png"),
        app_theme.get_pixbuf("mode/full_normal.png"),
        app_theme.get_pixbuf("mode/simple_hover.png"),
        app_theme.get_pixbuf("mode/full_hover.png"),
        app_theme.get_pixbuf("mode/simple_press.png"),
        app_theme.get_pixbuf("mode/full_press.png"),
        )
    return button

titlebar_button_dict = {
        # format : 'button_mask': (attr_name, button_widget _class, tooltip)
        'theme': ('theme_button', ThemeButton, _('Change skin')),
        'menu': ('menu_button', MenuButton, _('Main menu')),
        'max': ('max_button', MaxButton, _('Maximize')),
        'min': ('min_button', MinButton, _('Minimum')),
        'close': ('close_button', CloseButton, _('Close')),
        'mode': ('mode_button', create_revert_button, _('Toggle')),
        }

class Titlebar(EventBox):
    def __init__(self, 
                 button_mask=["theme", "menu", "max", "min", "close"],
                 icon_path=None,
                 app_name=None,
                 title=None,
                 add_separator=False,
                 height=26,
                 show_title=True,
                 enable_gaussian=True,
                 name_size=DEFAULT_FONT_SIZE,
                 title_size=DEFAULT_FONT_SIZE,
                 ):
        # Init.
        EventBox.__init__(self)
        self.set_size_request(-1, height)
        self.v_layout_box = gtk.VBox()
        self.h_layout_box = gtk.HBox()
        self.add(self.v_layout_box)
        self.v_layout_box.pack_start(self.h_layout_box, True, True)
        
        # Init separator.
        if add_separator:
            self.separator = gtk.HBox()
            self.separator.set_size_request(-1, 1)
            self.separator.connect("expose-event", self.expose_titlebar_separator)
            self.v_layout_box.pack_start(self.separator, True, True)
        
        # Add drag event box.
        self.drag_box = EventBox()
        self.h_layout_box.pack_start(self.drag_box, True, True)
        
        # Init left box to contain icon and title.
        self.left_box = gtk.HBox()
        self.drag_box.add(self.left_box)
        
        if show_title:
            # Add icon.
            if icon_path != None:
                self.icon_image_box = gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file(icon_path))
                self.icon_align = gtk.Alignment()
                self.icon_align.set(0.5, 0.5, 0.0, 0.0)
                self.icon_align.set_padding(5, 5, 5, 0)
                self.icon_align.add(self.icon_image_box)
                self.left_box.pack_start(self.icon_align, False, False)
                        
            # Add app name.
            if app_name == None:
                app_name_label = ""
            else:
                app_name_label = app_name
            self.app_name_box = Label(app_name_label, enable_gaussian=enable_gaussian, text_size=name_size)
            self.app_name_align = gtk.Alignment()
            self.app_name_align.set(0.5, 0.5, 0.0, 0.0)
            self.app_name_align.set_padding(2, 0, 5, 0)
            self.app_name_align.add(self.app_name_box)
            self.left_box.pack_start(self.app_name_align, False, False)
            
            # Add title.
            if title == None:
                title_label = ""
            else:
                title_label = title
            self.title_box = Label(
                title_label, enable_gaussian=enable_gaussian, 
                text_x_align=pango.ALIGN_CENTER,
                text_size=title_size,
                )
            self.title_align = gtk.Alignment()
            self.title_align.set(0.5, 0.5, 0.0, 0.0)
            self.title_align.set_padding(2, 0, 30, 30)
            self.title_align.add(self.title_box)
            self.left_box.pack_start(self.title_align, True, True)
            
        # Add button box.
        self.button_box = gtk.HBox()
        self.button_align = gtk.Alignment()
        self.button_align.set(1.0, 0.0, 0.0, 0.0)
        self.button_align.set_padding(0, 0, 0, 0)
        self.button_align.add(self.button_box)
        self.right_box = gtk.VBox()
        self.right_box.pack_start(self.button_align, False, False)
        self.h_layout_box.pack_start(self.right_box, False, False)
        
        # Add buttons.
        for mask in button_mask:
            setattr(self, titlebar_button_dict[mask][0], titlebar_button_dict[mask][1]())
            button = getattr(self, titlebar_button_dict[mask][0])
            self.button_box.pack_start(button, False, False, 1)
            Tooltip.text(button, titlebar_button_dict[mask][2]).show_delay(button, 2000)

        # Show.
        self.show_all()

    def expose_titlebar_separator(self, widget, event):
        '''
        Expose the separation line between the titlebar and the body of the window.

        @param widget: A widget of type Gtk.Widget.
        @param event: Not used.
        @return: Always return True.
        '''
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
    
        # Draw separator.
        cr.set_source_rgba(1, 1, 1, 0.5)
        draw_line(cr, rect.x + 1, rect.y + 2, rect.x + rect.width - 1, rect.y + 1)
    
        return True
    
    def change_name(self, name):
        '''
        Change the name of the application, which is displayed on the center of the title bar.
        
        @param name: New name string that want to set.
        '''
        self.app_name_box.set_text(name)
        
    def change_title(self, title):
        '''
        Change the title of the application, which is displayed on the center of the title bar.
        
        @param title: New title string that want to set.
        '''
        self.title_box.set_text(title)
        
gobject.type_register(Titlebar)

if __name__ == "__main__":
    
    def max_signal(w):    
        if window_is_max(w):
            win.unmaximize()
            print "min"
        else:
            win.maximize()
            print "max"

    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.connect("destroy", gtk.main_quit)
    tit = Titlebar()
    tit.max_button.connect("clicked", max_signal)
    win.add(tit.box)
    win.show_all()
    
    gtk.main()
