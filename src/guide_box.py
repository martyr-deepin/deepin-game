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

from dtk.ui.draw import draw_pixbuf, draw_vlinear
from dtk.ui.label import Label
from dtk.ui.box import BackgroundBox
from dtk.ui.theme import ui_theme, DynamicColor
from dtk.ui.threads import post_gui
from dtk.ui.scrolled_window import ScrolledWindow
from nls import _

import utils
from events import global_event

class GuideBox(gtk.VBox):
    def __init__(self):
        super(GuideBox, self).__init__()

        self.scrolled_window = ScrolledWindow()
        self.backgroundbox = BackgroundBox()
        self.backgroundbox.draw_mask = self.draw_mask

        self.guide_pixbuf = utils.get_common_image_pixbuf('guide.png')

        self.top_title = gtk.HBox()

        self.top_left_icon = gtk.VBox()
        self.top_left_icon.set_size_request(self.guide_pixbuf.get_width(), self.guide_pixbuf.get_height())
        self.top_left_icon.connect('expose-event', self.expose_top_left_icon)
        top_left_icon_align = gtk.Alignment(0.5, 0.5, 0, 0)
        top_left_icon_align.set_padding(15, 3, 13, 3)
        top_left_icon_align.add(self.top_left_icon)

        self.top_right_text = Label(_("游戏简介"), ui_theme.get_color('label_select_background'), 14)
        top_right_text_align = gtk.Alignment(0.5, 0.5, 0, 0)
        top_right_text_align.set_padding(18, 3, 3, 3)
        top_right_text_align.add(self.top_right_text)

        self.top_title.pack_start(top_left_icon_align, False, False)
        self.top_title.pack_start(top_right_text_align, False, False)

        self.content_box = gtk.VBox()
        self.guide_label = Label('', enable_select=False, wrap_width=200, text_size=9, text_color=DynamicColor('#808080'))
        guide_label_align = gtk.Alignment(0.5, 0.5, 1, 1)
        guide_label_align.set_padding(5, 5, 10, 10)
        guide_label_align.add(self.guide_label)
        self.content_box.pack_start(guide_label_align, False, False)

        self.backgroundbox.pack_start(self.top_title, False, False)
        self.backgroundbox.pack_start(self.content_box)

        self.scrolled_window.add_child(self.backgroundbox)
        self.add(self.scrolled_window)

        global_event.register_event('download-app-info-finish', self.update_content)

    @post_gui
    def update_content(self, js):
        self.guide_label.set_text(js['summary'])

    def draw_mask(self, cr, x, y, w, h):
        '''
        Draw mask interface.
        
        @param cr: Cairo context.
        @param x: X coordiante of draw area.
        @param y: Y coordiante of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        sidebar_color = "#ffffff"
        draw_vlinear(cr, x, y, w, h,
                     [(0, (sidebar_color, 0.9)),
                      (1, (sidebar_color, 0.9)),]
                     )
        
    def expose_top_left_icon(self, widget, event):
        # Init.
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        # Draw pkg icon.
        draw_pixbuf(cr,
                    self.guide_pixbuf,
                    rect.x,
                    rect.y)

