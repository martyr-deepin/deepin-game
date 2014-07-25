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
import os

from theme import app_theme
from nls import _, LANGUAGE
from constant import PROGRAM_VERSION
from utils import get_common_image_pixbuf

from dtk.ui.dialog import DialogBox
from dtk.ui.label import Label
from dtk.ui.theme import DynamicColor, ui_theme
from dtk.ui.line import HSeparator
from dtk.ui.button import Button
from dtk.ui.utils import set_clickable_cursor
from deepin_utils.process import run_command

class LinkButton(Label):
    def __init__(self, 
                 link,
                 text=None, 
                 enable_gaussian=False, 
                 text_color=ui_theme.get_color("link_text"),
                 ):
        '''
        Initialize LinkButton class.
        
        @param text: Link content.
        @param link: Link address.
        @param enable_gaussian: To enable gaussian effect on link, default is True.
        @param text_color: Link color, just use when option enable_gaussian is False.
        '''
        self.link = link
        self.text = text if text else self.link
        Label.__init__(self, self.text, text_color, enable_gaussian=enable_gaussian, text_size=9,
                       gaussian_radious=1, border_radious=0, underline=True)

        set_clickable_cursor(self)
        self.connect('button-press-event', self.button_press_action)

    def button_press_action(self, widget, e):
        if self.link:
            run_command('xdg-open %s' % self.link)

def create_separator_box(padding_x=0, padding_y=0):    
    separator_box = HSeparator(
        ui_theme.get_shadow_color("h_separator").get_color_info(),
        padding_x, padding_y)
    return separator_box

class AboutDialog(DialogBox):

    def __init__(self, title, cancel_callback=None):
        DialogBox.__init__(self, 
                title, 
                mask_type=2, 
                close_callback=self.dialog_close_action)
        self.connect('delete-event', self.dialog_close_action)
        self.set_size_request(480, 350)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        main_box = gtk.VBox(spacing=15)
        logo_image = gtk.image_new_from_pixbuf(get_common_image_pixbuf('logo24.png'))
        logo_name = Label(_("Deepin Game"), text_size=10)
        logo_box = gtk.HBox(spacing=2)
        logo_box.pack_start(logo_image, False, False)
        logo_box.pack_start(logo_name, False, False)
        
        version_label = Label(_("Version: "))
        version_content = Label(PROGRAM_VERSION, DynamicColor('#4D5154'))
        info_box = gtk.HBox(spacing=5)
        info_box.pack_start(version_label, False, False)
        info_box.pack_start(version_content, False, False)
        
        title_box = gtk.HBox()
        title_box.pack_start(logo_box, False, False)
        align = gtk.Alignment()
        align.set(0, 0, 0, 1)
        title_box.pack_start(align, True, True)
        title_box.pack_start(info_box, False, False)
        
        describe = _("Deepin Game is designed by Deepin for Linux users. Here "
                "you will elaborately find good and safe games selected by "
                "professionals. Click and play the best games you have ever "
                "seen. Deepin Game just for happiness!")
        
        describe_label = Label(describe, enable_select=False, wrap_width=430, text_size=10)
        main_box.pack_start(title_box, False, False)
        main_box.pack_start(create_separator_box(), False, True)
        main_box.pack_start(describe_label, False, False)

        links_table = gtk.Table(4, 2)

        links = [
                (_('Weibo: '), None, 'http://weibo.com/linuxdeepinnew'),
                (_('Forum: '), None, 'http://www.linuxdeepin.com/forum'),
                (_('Feedback: '), None, 'http://www.linuxdeepin.com/mantis'),
                (_('Game upload: '), 'game@linuxdeepin.com', 'mailto:game@linuxdeepin.com'),
                ]
        for (i, l) in enumerate(links):
            left_text = Label(l[0])
            left_text_align = self.create_right_align()
            left_text_align.add(left_text)
            right_link = LinkButton(text=l[1], link=l[2])
            links_table.attach(left_text_align, 0, 1, i, i+1, xoptions=gtk.FILL, xpadding=5, ypadding=4)
            links_table.attach(right_link, 1, 2, i, i+1, xoptions=gtk.FILL)
            #main_box.pack_start(self.create_link_box(l[0], l[1], l[2]), False, False)
        
        main_box.pack_start(links_table, False, False)
        main_align = gtk.Alignment()
        main_align.set_padding(20, 0, 20, 20)
        main_align.set(0, 0, 1, 1)
        main_align.add(main_box)
        self.body_box.pack_start(main_align)

        self.ok_button = Button(_('Close'))
        self.ok_button.connect('clicked', self.dialog_close_action)
        ok_button_align = gtk.Alignment(0.5, 0.5, 0, 0)
        ok_button_align.set_padding(9, 11, 0, 10)
        ok_button_align.add(self.ok_button)
        self.right_button_box.pack_start(ok_button_align, False, False)

    def create_right_align(self):
        align = gtk.Alignment(1, 0.5, 0, 0)
        return align

    def create_link_box(self, text, link_text, link):
        box = gtk.HBox()

        label = Label(text)
        box.pack_start(label, False, False)

        link_button = LinkButton(link=link, text=link_text)
        box.pack_start(link_button, False, False)

        return box
        
    def dialog_close_action(self, widget=None, event=None):
        self.hide_all()
        return True

if __name__ == '__main__':
    AboutDialog('About Deepin Games').show_all()
    gtk.main()
