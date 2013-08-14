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
import pango
from dtk.ui.theme import DynamicColor, ui_theme
from dtk.ui.constant import DEFAULT_FONT_SIZE
from dtk.ui.utils import get_content_size, propagate_expose
from dtk.ui.draw import draw_pixbuf, draw_text

class Button(gtk.Button):

    def __init__(self, 
                pixbuf_normal,
                pixbuf_hover,
                pixbuf_press,
                button_label=None, 
                label_color=None,
                padding_x=0, 
                font_size=DEFAULT_FONT_SIZE):

        gtk.Button.__init__(self)
        self.pixbuf_normal = pixbuf_normal
        self.pixbuf_hover = pixbuf_hover
        self.pixbuf_press = pixbuf_press
        self.font_size = font_size

        if not label_color:
            label_dcolor = ui_theme.get_color("button_default_font")
        else:
            label_dcolor = DynamicColor(label_color)
        self.button_press_flag = False
        
        # Init request size.
        label_width = 0
        button_width = pixbuf_normal.get_pixbuf().get_width()
        button_height = pixbuf_normal.get_pixbuf().get_height()

        if button_label:
            label_width = get_content_size(button_label, self.font_size)[0]

        self.set_size_request(button_width + label_width + padding_x * 2,
                              button_height)
        
        self.connect("button-press-event", self.press_button)
        self.connect("button-release-event", self.release_button)
        
        # Expose button.
        self.connect("expose-event", lambda w, e : self.expose_button(
                w, e,
                button_label, padding_x, self.font_size, label_dcolor))
        
    def press_button(self, widget, event):    
        self.button_press_flag = True
        self.queue_draw()
        
    def release_button(self, widget, event):    
        self.button_press_flag = False
        self.queue_draw()    
        
    def expose_button(self, widget, event, 
                             button_label, padding_x, font_size, label_dcolor):
        # Init.
        rect = widget.allocation
        image = self.pixbuf_normal.get_pixbuf()
        
        # Get pixbuf along with button's sate.
        if widget.state == gtk.STATE_NORMAL:
            image = self.pixbuf_normal.get_pixbuf()
        elif widget.state == gtk.STATE_PRELIGHT:
            image = self.pixbuf_hover.get_pixbuf()
        elif widget.state == gtk.STATE_ACTIVE:
            image = self.pixbuf_press.get_pixbuf()
        
        # Draw button.
        cr = widget.window.cairo_create()
        draw_pixbuf(cr, image, rect.x + padding_x, rect.y)
        
        # Draw font.
        if widget.state == gtk.STATE_INSENSITIVE:
            label_color = ui_theme.get_color("disable_text").get_color()
        else:
            label_color = label_dcolor.get_color()
        if button_label:
            draw_text(cr, button_label, 
                        rect.x + image.get_width() + padding_x * 2,
                        rect.y, 
                        rect.width - image.get_width() - padding_x * 2,
                        rect.height,
                        font_size, 
                        label_color,
                        alignment=pango.ALIGN_LEFT
                        )
    
        # Propagate expose to children.
        propagate_expose(widget, event)
        
        return True

class ToggleButton(gtk.ToggleButton):
    '''
    ToggleButton class.
    
    @undocumented: press_toggle_button
    @undocumented: release_toggle_button
    @undocumented: expose_toggle_button
    @undocumented: set_inactive_pixbuf_group
    @undocumented: set_active_pixbuf_group
    '''
	
    def __init__(self, 
                 inactive_normal_dpixbuf, 
                 active_normal_dpixbuf, 
                 inactive_hover_dpixbuf=None, 
                 active_hover_dpixbuf=None, 
                 inactive_press_dpixbuf=None, 
                 active_press_dpixbuf=None,
                 inactive_disable_dpixbuf=None, 
                 active_disable_dpixbuf=None,
                 button_label=None, 
                 label_color=None,
                 padding_x=0, 
                 font_size=DEFAULT_FONT_SIZE):
        '''
        Initialize ToggleButton class.
        
        @param inactive_normal_dpixbuf: DynamicPixbuf for inactive normal status. 
        @param active_normal_dpixbuf: DynamicPixbuf for active normal status. 
        @param inactive_hover_dpixbuf: DynamicPixbuf for inactive hover status, default is None. 
        @param active_hover_dpixbuf: DynamicPixbuf for active hover status, default is None. 
        @param inactive_press_dpixbuf: DynamicPixbuf for inactive press status, default is None. 
        @param active_press_dpixbuf: DynamicPixbuf for active press status, default is None. 
        @param inactive_disable_dpixbuf: DynamicPixbuf for inactive disable status, default is None. 
        @param active_disable_dpixbuf: DynamicPixbuf for active disable status, default is None. 
        @param button_label: Button label, default is None.
        @param padding_x: Padding x, default is 0.
        @param font_size: Font size, default is DEFAULT_FONT_SIZE.
        '''
        gtk.ToggleButton.__init__(self)
        self.font_size = font_size
        if not label_color:
            label_dcolor = ui_theme.get_color("button_default_font")
        else:
            label_dcolor = DynamicColor(label_color)
        self.button_press_flag = False
        
        self.inactive_pixbuf_group = (inactive_normal_dpixbuf,
                                      inactive_hover_dpixbuf,
                                      inactive_press_dpixbuf,
                                      inactive_disable_dpixbuf)
        
        self.active_pixbuf_group = (active_normal_dpixbuf,
                                    active_hover_dpixbuf,
                                    active_press_dpixbuf,
                                    active_disable_dpixbuf)

        # Init request size.
        label_width = 0
        button_width = inactive_normal_dpixbuf.get_pixbuf().get_width()
        button_height = inactive_normal_dpixbuf.get_pixbuf().get_height()
        if button_label:
            label_width = get_content_size(button_label, self.font_size)[0]
        self.set_size_request(button_width + label_width + padding_x * 2,
                              button_height)
        
        self.connect("button-press-event", self.press_toggle_button)
        self.connect("button-release-event", self.release_toggle_button)
        
        # Expose button.
        self.connect("expose-event", lambda w, e : self.expose_toggle_button(
                w, e,
                button_label, padding_x, self.font_size, label_dcolor))
        
    def press_toggle_button(self, widget, event):    
        '''
        Callback for `button-press-event` signal.
        
        @param widget: ToggleButton widget.
        @param event: Button press event.
        '''
        self.button_press_flag = True
        self.queue_draw()
        
    def release_toggle_button(self, widget, event):    
        '''
        Callback for `button-press-release` signal.
        
        @param widget: ToggleButton widget.
        @param event: Button release event.
        '''
        self.button_press_flag = False
        self.queue_draw()    
        
    def expose_toggle_button(self, widget, event, 
                             button_label, padding_x, font_size, label_dcolor):
        '''
        Callback for `expose-event` signal.
        
        @param widget: ToggleButton widget.
        @param event: Expose event.
        @param button_label: Button label string.
        @param padding_x: horticultural padding value.
        @param font_size: Font size.
        @param label_dcolor: Label DynamicColor.
        '''
        # Init.
        inactive_normal_dpixbuf, inactive_hover_dpixbuf, inactive_press_dpixbuf, inactive_disable_dpixbuf = self.inactive_pixbuf_group
        active_normal_dpixbuf, active_hover_dpixbuf, active_press_dpixbuf, active_disable_dpixbuf = self.active_pixbuf_group
        rect = widget.allocation
        image = inactive_normal_dpixbuf.get_pixbuf()
        
        # Get pixbuf along with button's sate.
        if widget.state == gtk.STATE_INSENSITIVE:
            if widget.get_active():
                image = active_disable_dpixbuf.get_pixbuf()
            else:
                image = inactive_disable_dpixbuf.get_pixbuf()
        elif widget.state == gtk.STATE_NORMAL:
            image = inactive_normal_dpixbuf.get_pixbuf()
        elif widget.state == gtk.STATE_PRELIGHT:
            if not inactive_hover_dpixbuf and not active_hover_dpixbuf:
                if widget.get_active():
                    image = active_normal_dpixbuf.get_pixbuf()
                else:    
                    image = inactive_normal_dpixbuf.get_pixbuf()
            else:    
                if inactive_hover_dpixbuf and active_hover_dpixbuf:
                    if widget.get_active():
                        image = active_hover_dpixbuf.get_pixbuf()
                    else:    
                        image = inactive_hover_dpixbuf.get_pixbuf()
                elif inactive_hover_dpixbuf:        
                    image = inactive_hover_dpixbuf.get_pixbuf()
                elif active_hover_dpixbuf:    
                    image = active_hover_dpixbuf.get_pixbuf()
        elif widget.state == gtk.STATE_ACTIVE:
            if inactive_press_dpixbuf and active_press_dpixbuf:
                if self.button_press_flag:
                    if widget.get_active():
                        image = active_press_dpixbuf.get_pixbuf()
                    else:    
                        image = inactive_press_dpixbuf.get_pixbuf()
                else:    
                    image = active_normal_dpixbuf.get_pixbuf()
            else:        
                image = active_normal_dpixbuf.get_pixbuf()
        
        # Draw button.
        cr = widget.window.cairo_create()
        draw_pixbuf(cr, image, rect.x + padding_x, rect.y)
        
        # Draw font.
        if widget.state == gtk.STATE_INSENSITIVE:
            label_color = ui_theme.get_color("disable_text").get_color()
        else:
            label_color = label_dcolor.get_color()
        if button_label:
            draw_text(cr, button_label, 
                        rect.x + image.get_width() + padding_x * 2,
                        rect.y, 
                        rect.width - image.get_width() - padding_x * 2,
                        rect.height,
                        font_size, 
                        label_color,
                        alignment=pango.ALIGN_LEFT
                        )
    
        # Propagate expose to children.
        propagate_expose(widget, event)
        
        return True
    
    def set_inactive_pixbuf_group(self, new_group):
        '''
        Set inactive pixbuf group.
        
        @param new_group: Inactive pixbuf group.
        '''
        self.inactive_pixbuf_group = new_group
        
    def set_active_pixbuf_group(self, new_group):    
        '''
        Set inactive pixbuf group.
        
        @param new_group: Active pixbuf group.
        '''
        self.active_pixbuf_group = new_group

