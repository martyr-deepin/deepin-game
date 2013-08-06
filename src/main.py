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

import os
import sys
import gtk
import webkit
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import subprocess

from theme import app_theme
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.application import Application
from dtk.ui.statusbar import Statusbar
from dtk.ui.label import Label
from dtk.ui.theme import DynamicPixbuf
from deepin_utils.file import get_parent_dir

from navigatebar import Navigatebar
from utils import get_common_image
from constant import (
        GAME_CENTER_DBUS_NAME,
        GAME_CENTER_DBUS_PATH,
        CACHE_DIR,
        GAME_CENTER_SERVER_ADDRESS,
        )
from nls import _

class GameCenterApp(dbus.service.Object):

    def __init__(self, session_bus):
        dbus.service.Object.__init__(self, session_bus, GAME_CENTER_DBUS_PATH)

        self.init_ui()

    def init_ui(self):
        self.application = Application()
        self.application.set_default_size(1000, 660)
        self.application.set_skin_preview(get_common_image("frame.png"))
        self.application.set_icon(get_common_image("logo48.png"))
        self.application.add_titlebar(
                ["theme", "menu", "max","min", "close"],
                show_title=False
                )
        self.application.window.set_title(_("Deepin Game Center"))

        # Init page box.
        self.page_box = gtk.VBox()
        
        # Init page align.
        self.page_align = gtk.Alignment()
        self.page_align.set(0.5, 0.5, 1, 1)
        self.page_align.set_padding(0, 0, 2, 2)
        
        # Append page to switcher.
        self.page_align.add(self.page_box)
        self.application.main_box.pack_start(self.page_align, True, True)
        
        # Init status bar.
        self.statusbar = Statusbar(24)
        status_box = gtk.HBox()
        self.message_box = gtk.HBox()

        self.message_label = Label("Version 1.0", enable_gaussian=True)
        label_align = gtk.Alignment()
        label_align.set(0.0, 0.5, 0, 0)
        label_align.set_padding(0, 0, 10, 0)
        label_align.add(self.message_label)
        self.message_box.pack_start(label_align)

        status_box.pack_start(self.message_box, True, True)
        self.statusbar.status_box.pack_start(status_box, True, True)
        self.application.main_box.pack_start(self.statusbar, False, False)

        self.webview = webkit.WebView()
        self.webview.set_transparent(True)
        self.webview.connect('navigation-policy-decision-requested', self.navigation_policy_decision_requested_cb)
        
        self.webview.load_uri(GAME_CENTER_SERVER_ADDRESS+'game')

        self.page_box.add(self.webview)
        
        self.navigatebar = Navigatebar(
                [
                (None, _("首页"), self.show_home_page),
                (None, _("游戏专题"), self.show_subject_page),
                (None, _("我的游戏"), self.show_mygame_page),
                ],
                font_size = 11,
                padding_x = 5,
                padding_y = 16,
                vertical=False,
                item_normal_pixbuf=DynamicPixbuf(get_common_image('top/nav_normal.png')),
                item_hover_pixbuf=DynamicPixbuf(get_common_image('top/nav_hover.png')),
                item_press_pixbuf=DynamicPixbuf(get_common_image('top/nav_press.png')),
                )
        self.navigatebar.set_size_request(-1, 56)
        self.navigatebar_align = gtk.Alignment(0, 0, 1, 1)
        self.navigatebar_align.set_padding(0, 0, 4, 0)
        self.navigatebar_align.add(self.navigatebar)
        self.application.titlebar.set_size_request(-1, 56)
        self.application.titlebar.left_box.pack_start(self.navigatebar_align, True, True)
        self.application.window.add_move_event(self.navigatebar)

    def navigation_policy_decision_requested_cb(self, web_view, frame, request, navigation_action, policy_decision):
        uri = request.get_uri()
        if uri.startswith('http://') or uri.startswith('https://'):
            return False
        else:
            self.uri_handle(uri)
            return True

    def uri_handle(self, uri):
        order, data = uri.split('://')
        if order == 'play':
            self.show_play(data)
        elif order == 'star':
            self.toggle_favorite(data)

    def show_play(self, data):
        appid = data.strip()
        player_path = os.path.join(get_parent_dir(__file__), 'player.py')
        subprocess.Popen(['python', player_path, appid], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

    def toggle_favorite(self, data):
        pass

    def show_home_page(self):
        self.webview.load_uri(GAME_CENTER_SERVER_ADDRESS+'game')

    def show_subject_page(self):
        pass

    def show_mygame_page(self):
        pass

    def run(self):
        self.application.run()

    @dbus.service.method(GAME_CENTER_DBUS_NAME, in_signature="", out_signature="")    
    def hello(self):
        self.application.window.present()

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    
    if is_dbus_name_exists(GAME_CENTER_DBUS_NAME, True):
        print "deepin game center has running!"
        
        bus_object = session_bus.get_object(GAME_CENTER_DBUS_NAME,
                                            GAME_CENTER_DBUS_PATH)
        bus_interface = dbus.Interface(bus_object, GAME_CENTER_DBUS_NAME)
        bus_interface.hello()
        
    else:
        # Init dbus.
        bus_name = dbus.service.BusName(GAME_CENTER_DBUS_NAME, session_bus)
            
        try:
            GameCenterApp(session_bus).run()
        except KeyboardInterrupt:
            pass

