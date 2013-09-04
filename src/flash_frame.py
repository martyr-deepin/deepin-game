#!/usr/bin/env python
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
import gtk
import glib
from deepin_utils.ipc import is_dbus_name_exists
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import dbus.service
from dtk.ui.browser import WebView
import json
from paned_box import PanedBox
from constant import COOKIE_FILE

from deepin_utils.file import get_parent_dir

static_dir = os.path.join(get_parent_dir(__file__, 2), "static")

class FlashFrame(dbus.service.Object):
    '''
    class docs
    '''
	
    def __init__(self, session_bus, appid, dbus_name, dbus_path):
        dbus.service.Object.__init__(self, session_bus, dbus_path)

        self.appid = appid
        self.dbus_name = dbus_name
        self.dbus_path = dbus_path
        
        # WARING: only use once in one process
        DBusGMainLoop(set_as_default=True) 
        
        self.plug = gtk.Plug(0)

        self.webview = WebView(COOKIE_FILE)
        self.webview.connect('title-changed', self.title_change_handler)
        #self.webview.enable_inspector()
        self.paned_box = PanedBox(2, True, 2, True)
        self.paned_box.enter_bottom_win_callback = self.enter_bottom_notify
        self.paned_box.enter_top_win_callback = self.enter_top_notify
        self.paned_box.add_content_widget(self.webview)
        self.plug.add(self.paned_box)
        
        # Handle signals.
        self.plug.connect("realize", self.flash_frame_realize)
        self.plug.connect("destroy", self.flash_frame_exit)

        glib.timeout_add(1000, self.is_exist)
        glib.timeout_add(200, self.connect_signal)

        def message_receiver(self, *message):
            message_type, contents = message
            if message_type == 'exit':
                self.exit()
            elif message_type == 'load_uri':
                self.load_flash(contents)
            elif message_type == 'load_loading_uri':
                self.webview.load_uri(contents)
                self.send_message('loading_uri_finish', '')
            elif message_type == 'load_string':
                self.webview.load_string(contents)
            elif message_type == 'get_plug_id':
                self.send_flash_info()
            elif message_type == 'app_info_download_finish':
                self.webview.execute_script("app_info=%s" %
                        json.dumps(str(contents), encoding="UTF-8", ensure_ascii=False))

        setattr(FlashFrame, 
                'message_receiver', 
                dbus.service.method(dbus_name)(message_receiver))

    def title_change_handler(self, widget, frame, new_title):
        if new_title == 'finish_load':
            self.webview.execute_script('loading_flash(%s)' %
                json.dumps(self.swf_info, encoding="UTF-8", ensure_ascii=False))

    def load_flash(self, contents):
        flash_html_path = os.path.join(static_dir, 'flash.html')
        self.webview.load_uri("file://" + flash_html_path)
        self.swf_info = str(contents).split(',')

    def enter_bottom_notify(self):
        self.send_message('enter_bottom', '')

    def enter_top_notify(self):
        self.send_message('enter_top', '')

    def is_exist(self):
        if dbus.SessionBus().name_has_owner("com.deepin.game_player_%s" % self.appid):
            return True
        else:
            glib.timeout_add(0, gtk.main_quit)
            return False

    def run(self):    
        self.plug.show_all()
        self.paned_box.bottom_window.set_composited(True)
        self.paned_box.top_window.set_composited(True)
        gtk.main()

    def do_delete_event(self, w):
        #a trick to prevent plug destroyed!.  the  better way is recreate an GtkPlug when need reuse it's content
        return True

    def flash_frame_realize(self, widget):
        # Send module information.
        self.send_flash_info()

    def exit(self):
        gtk.main_quit()

    def flash_frame_exit(self, widget):
        gtk.main_quit()
        
    def send_message(self, message_type, message_content):
        session_bus = dbus.SessionBus()
        GAME_PLAYER_DBUS_NAME = "com.deepin.game_player_%s" % self.appid
        GAME_PLAYER_DBUS_PATH = "/com/deepin/game_player_%s" % self.appid
        if is_dbus_name_exists(GAME_PLAYER_DBUS_NAME):

            bus_object = session_bus.get_object(GAME_PLAYER_DBUS_NAME, GAME_PLAYER_DBUS_PATH)
            method = bus_object.get_dbus_method("message_receiver")
            method(message_type, 
                   message_content,
                   reply_handler=self.handle_dbus_reply, # add reply handler
                   error_handler=self.handle_dbus_error  # add error handler
                   )

    def connect_signal(self):
        session_bus = dbus.SessionBus()
        GAME_PLAYER_DBUS_NAME = "com.deepin.game_player_%s" % self.appid
        GAME_PLAYER_DBUS_PATH = "/com/deepin/game_player_%s" % self.appid
        if is_dbus_name_exists(GAME_PLAYER_DBUS_NAME):
            session_bus.add_signal_receiver(
                    self.signal_receiver, 
                    signal_name="update_signal", 
                    dbus_interface=GAME_PLAYER_DBUS_NAME, 
                    path=GAME_PLAYER_DBUS_PATH)
            return False
        else:
            return True

    def signal_receiver(self, message):
        message_type, contents = message
        if message_type == 'download_update':
            self.webview.execute_script('fresh_loading(%s)' % 
                    json.dumps(str(contents), encoding="UTF-8", ensure_ascii=False))
        elif message_type == 'download_finish':
            self.load_flash(str(contents))
        elif message_type == 'load_uri':
            self.webview.execute_script("window.location.href = %s" %
                    json.dumps(str(contents).split(',')[0], encoding="UTF-8", ensure_ascii=False))
            
    def handle_dbus_reply(self, *reply):
        # print "%s (reply): %s" % (self.module_dbus_name, str(reply))
        pass
        
    def handle_dbus_error(self, *error):
        #print "%s (error): %s" % (self.module_dbus_name, str(error))
        pass
        
    def send_flash_info(self):
        self.send_message("send_plug_id", (self.appid, self.plug.get_id()))

if __name__ == '__main__':
    import sys

    DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    appid = sys.argv[1]
    FLASH_DBUS_NAME = "com.deepin.game_flash_%s" % (appid)
    FLASH_DBUS_PATH = "/com/deepin/game_flash_%s" % (appid)

    if is_dbus_name_exists(FLASH_DBUS_NAME, True):
        print "deepin game %s has running!" % appid
        bus_object = session_bus.get_object(FLASH_DBUS_NAME, FLASH_DBUS_PATH)
    else:
        bus_name = dbus.service.BusName(FLASH_DBUS_NAME, session_bus)
        try:
            FlashFrame(session_bus, appid, FLASH_DBUS_NAME, FLASH_DBUS_PATH).run()
        except KeyboardInterrupt:
            pass
