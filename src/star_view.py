#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
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
from dtk.ui.draw import draw_pixbuf, draw_text
from dtk.ui.utils import propagate_expose, get_event_coords, get_content_size

import utils

STAR_SIZE = utils.get_common_image_pixbuf('star/star_on.png').get_width()

class StarBuffer(gobject.GObject):
    '''
    StarBuffer class.
    
    @undocumented: get_star_pixbufs
    '''
	
    def __init__(self, 
                 star_level=5,
                 ):
        '''
        Initialize StarBuffer class.
        
        @param star_level: The level of star, default is 5.
        '''
        gobject.GObject.__init__(self)
        self.star_level = star_level
        
    def render(self, cr, rect):
        '''
        Render star buffer on given cairo and rectangle.
        
        @param cr: The cairo object.
        @param rect: The render rectangle.
        '''
        for (star_index, star_pixbuf) in enumerate(self.get_star_pixbufs()):
            draw_pixbuf(cr,
                        star_pixbuf,
                        rect.x + star_index * STAR_SIZE,
                        rect.y + (rect.height - star_pixbuf.get_height()) / 2,
                        )
            
    def get_star_pixbufs(self):
        star_paths = ["star_off.png"] * 5

        for index in range(0, int(self.star_level / 2)):
            star_paths[index] = "star_on.png"
            
        if int(self.star_level % 2) == 1:
            star_paths[int(self.star_level / 2)] = "star_half.png"
                
        return map(lambda path: utils.get_common_image_pixbuf("star/%s" % path), star_paths)        
        
gobject.type_register(StarBuffer)        

class StarView(gtk.Button):
    '''
    StarView class.
    
    @undocumented: expose_star_view
    @undocumented: motion_notify_star_view
    '''
	
    def __init__(self, star_level=5):
        '''
        Initialize StarView class.
        '''
        gtk.Button.__init__(self)
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.star_buffer = StarBuffer()
        self.read_only = False
        self.star_level = star_level
        
        self.set_size_request(STAR_SIZE * 5, STAR_SIZE)
        
        self.connect("enter-notify-event", self.enter_notify_star_view)
        self.connect("leave-notify-event", self.leave_notify_star_view)
        self.connect("motion-notify-event", self.motion_notify_star_view)
        self.connect("expose-event", self.expose_star_view)        

    def set_star_level(self, star_level):
        self.star_level = star_level
        self.star_buffer.star_level = star_level
        self.queue_draw()

    def set_read_only(self, b):
        if b:
            self.read_only = True
            self.star_buffer.star_level = self.star_level
            self.queue_draw()
        else:
            self.read_only = False
        
    def expose_star_view(self, widget, event):
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        self.star_buffer.render(cr, rect)
        
        # Propagate expose.
        propagate_expose(widget, event)
        
        return True
    
    def motion_notify_star_view(self, widget, event):
        if not self.read_only:
            (event_x, event_y) = get_event_coords(event)
            self.star_buffer.star_level = int(min(event_x / (STAR_SIZE / 2) + 1, 10))
            self.queue_draw()

    def enter_notify_star_view(self, widget, event):
        pass

    def leave_notify_star_view(self, widget, event):
        self.star_buffer.star_level = self.star_level
        self.queue_draw()
        
gobject.type_register(StarView)        

class StarMark(gtk.VBox):
    def __init__(self, star, size):
        gtk.VBox.__init__(self)
        self._star = star
        self.size = size

        self.font_step = 3
        
        self.int_n, self.float_n = self.get_split_star()
        self.int_n_width, self.height = get_content_size("<b>%s</b>" % self.int_n, self.size)
        self.float_n_width, self.float_n_height = get_content_size("."+self.float_n, self.size-self.font_step)
        self.width = self.int_n_width + self.float_n_width
        self.height = self.height
        self.set_size_request(self.width, self.height)

        self.connect("expose-event", self.expose_star_mark)

    @property
    def star(self):
        return self._star

    def update_star(self, star):
        self._star = star
        self.queue_draw()

    def get_split_star(self):
        int_n, float_n = str(round(self._star, 1)).split('.')
        return (int_n, float_n)

    def expose_star_mark(self, widget, event):
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        # draw integer
        draw_text(
            cr, 
            "<b>%s</b>" % self.get_split_star()[0],
            rect.x,
            rect.y,
            self.int_n_width,
            self.height,
            text_size=self.size,
            text_color="#FFFFFF"
            )

        # draw decimals
        draw_text(
            cr, 
            "." + self.get_split_star()[1],
            rect.x + self.int_n_width,
            rect.y + self.height-self.float_n_height - 1,
            self.float_n_width,
            self.float_n_height,
            text_size=self.size-self.font_step,
            text_color="#FFFFFF"
            )

gobject.type_register(StarMark)
