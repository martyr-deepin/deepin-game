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
import cairo
import gobject
from dtk.ui.draw import draw_pixbuf, draw_text
from dtk.ui.utils import (
        propagate_expose, 
        get_event_coords, 
        get_content_size, 
        get_widget_root_coordinate,
        WIDGET_POS_TOP_LEFT,
        )

import utils
from ui_utils import draw_round_rectangle_with_triangle
from nls import _

SHADOW_VALUE = 2 
ARROW_WIDTH = 10
ARROW_HEIGHT = ARROW_WIDTH / 2

from dtk_cairo_blur import gaussian_blur
from dtk.ui.utils import alpha_color_hex_to_cairo

class progressBarTip(gtk.Window):
    '''
    class docs
    '''
	
    def __init__(self):
        '''
        init docs
        '''
        gtk.Window.__init__(self)
        
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap() or 
                          gtk.gdk.Screen().get_rgb_colormap())
        
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_position(gtk.WIN_POS_NONE)
        
        self.surface = None
        self.surface_x = SHADOW_VALUE
        self.surface_y = SHADOW_VALUE
        self.surface_border = SHADOW_VALUE
        self.arrow_width = ARROW_WIDTH
        self.arrow_height = ARROW_HEIGHT
        self.radius = 2
        self.pos_type = gtk.POS_BOTTOM
        self.offset = 45
        self.reset_surface_flag = False

        self.font_size = 9
        self.content_top_padding = 10

        self.pixbuf = None
        self.pixbuf_width = 0
        self.pixbuf_height = 0
        
        self.content = "03:12"
        self.text_size = get_content_size(self.content, self.font_size)
        self.width, self.height = (self.text_size[0] + 26, self.text_size[1] + 18 + self.arrow_height)
        self.shadow_color = ("#000000", 0.6)
        self.mask_color = ("#ffffff", 0.8)
        self.border_out_color = ("#000000", 1.0)
        self.set_redraw_on_allocate(True)
        
        self.drawing = gtk.Alignment()
        self.drawing.set_redraw_on_allocate(True)
        self.drawing.connect("expose-event", self.on_expose_event)
        self.add(self.drawing)

        self.set_size_request(90, 40)

    def set_content(self, content):
        self.content = content
        self.resize(1, 1)
        self.text_size = get_content_size(self.content, self.font_size)
        self.width, self.height = (self.text_size[0] + 26, self.text_size[1] + 18 + self.arrow_height)
        self.set_geometry_hints(None, self.width, self.height, self.width, self.height, \
                -1, -1, -1, -1, -1, -1)
        self.offset = (self.width - self.arrow_width) / 2
        self.queue_draw()

    def show_image_text(self, text, image_path):
        self.content = text
        self.text_size = get_content_size(self.content, self.font_size)
        self.pixbuf = utils.get_common_image_pixbuf(image_path)
        self.width, self.height = 136, 78
        self.offset = (self.width - self.arrow_width) / 2
        self.set_geometry_hints(None, self.width, self.height, self.width, self.height, \
                -1, -1, -1, -1, -1, -1)
        self.queue_draw()
        
    def compute_shadow(self, rect):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, rect.width, rect.height)
        surface_cr = cairo.Context(self.surface)
        
        draw_round_rectangle_with_triangle(surface_cr, 
                                           rect,
                                           self.radius, 
                                           self.arrow_width, self.arrow_height, self.offset,
                                           border=5,
                                           pos_type=self.pos_type)
        
        surface_cr.set_line_width(2)
        surface_cr.set_source_rgba(*alpha_color_hex_to_cairo(self.shadow_color))
        surface_cr.stroke_preserve()
        gaussian_blur(self.surface, 2)
        
        # border.
        # out border.
        surface_cr.clip()
        draw_round_rectangle_with_triangle(surface_cr, 
                                           rect,
                                           self.radius, 
                                           self.arrow_width, self.arrow_height, self.offset,
                                           border=6,
                                           pos_type=self.pos_type)
        surface_cr.set_source_rgba(*alpha_color_hex_to_cairo(self.mask_color))
        surface_cr.set_line_width(1)
        surface_cr.fill()
        
        # in border.
        # surface_cr.reset_clip()
        # draw_round_rectangle_with_triangle(surface_cr, 
        #                                    rect,
        #                                    self.radius, 
        #                                    self.arrow_width, self.arrow_height, self.offset,
        #                                    border=2,
        #                                    pos_type=self.pos_type) 
        
        # surface_cr.set_source_rgba(1, 1, 1, 1.0) # set in border color.
        # surface_cr.set_line_width(self.border_width)
        # surface_cr.fill()
        
    def on_expose_event(self, widget, event):
        '''
        docs
        '''
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(1, 1, 1, 0)
        cr.rectangle(*rect)
        cr.paint()
        
        cr.set_operator(cairo.OPERATOR_OVER)
        
        
        #if not self.surface or self.reset_surface_flag:
        self.compute_shadow(rect)
        cr.set_source_surface(self.surface, 0, 0)    
        cr.paint()

        text_top_padding = (rect.height - self.text_size[1] - ARROW_HEIGHT)/2
        if self.pixbuf:
            draw_pixbuf(cr, self.pixbuf, rect.x + (rect.width - self.pixbuf.get_width())/2, rect.y + self.content_top_padding)
            text_top_padding = self.content_top_padding + 2 + self.pixbuf.get_height()
        
        draw_text(
                cr, 
                self.content, 
                rect.x + (rect.width - self.text_size[0])/2, 
                rect.y + text_top_padding, 
                self.text_size[0], 
                self.text_size[1],
                self.font_size, 
                "#707070", 
                )
        
        return True
    
    def reset_surface(self):
        self.reset_surface_flag = True
        
    def move_to(self, x, y):
        self.move(int(x - self.width / 2), int(y - self.height + 3))

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

    __gsignals__ = {
        "star-press" : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,)),
    }

	
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

        self.progressbar_tip = progressBarTip()
        
        self.connect("leave-notify-event", self.leave_notify_star_view)
        self.connect("motion-notify-event", self.motion_notify_star_view)
        self.connect("expose-event", self.expose_star_view)        
        #self.connect("button-press-event", self.star_button_press_handler)


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
            self.queue_draw()

    def star_button_press_handler(self, widget, event):
        (event_x, event_y) = get_event_coords(event)
        self.emit('star-press', int(min(event_x / (STAR_SIZE / 2) + 1, 10)))
        
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
            star_level = int(min(event_x / (STAR_SIZE / 2) + 1, 10))
            self.star_buffer.star_level = star_level
            self.show_progressbar_tip(event)
            if star_level == 1 or star_level == 2:
                tips = _('Boring')
            elif star_level == 3 or star_level == 4:
                tips = _('Nothing special')
            elif star_level == 5 or star_level == 6:
                tips = _('Interesting')
            elif star_level == 7 or star_level == 8:
                tips = _('Good')
            elif star_level == 9 or star_level == 10:
                tips = _('Wow, wonderful')
            self.progressbar_tip.set_content(tips)
            self.queue_draw()

    def leave_notify_star_view(self, widget, event):
        self.hide_progressbar_tip()

        self.star_buffer.star_level = self.star_level
        self.queue_draw()

    def show_progressbar_tip(self, event):
        self.progressbar_tip.move_to(*self.adjust_event_coords(event))
        self.progressbar_tip.show_all()

    def hide_progressbar_tip(self):    
        self.progressbar_tip.hide_all()

    def adjust_event_coords(self, event):
        _, y = get_widget_root_coordinate(self, pos_type=WIDGET_POS_TOP_LEFT)
        x, _ = event.get_root_coords()
        return x, y
        
gobject.type_register(StarView)        

if __name__ == '__main__':
    tip = progressBarTip()
    tip.show_image_text('您今天已评过', 'star/star_finish.png')
    #tip.set_content('测试一下')
    tip.move(768, 300)
    tip.show_all()
    gtk.main()
