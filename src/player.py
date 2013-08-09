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
import gtk
import gobject
import subprocess
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import urllib

from theme import app_theme
from dtk.ui.application import Application
from dtk.ui.statusbar import Statusbar
from dtk.ui.label import Label
from deepin_utils.file import get_parent_dir, touch_file_dir
from deepin_utils.ipc import is_dbus_name_exists

from utils import get_common_image, handle_dbus_reply, handle_dbus_error
import utils
from nls import _
from constant import GAME_CENTER_DATA_ADDRESS
from download_manager import fetch_service, TaskObject
from xdg_support import get_config_file

info_data = os.path.join(get_parent_dir(__file__, 2), "data", "info.db")
static_dir = os.path.join(get_parent_dir(__file__, 2), "static")

class Player(dbus.service.Object):
    def __init__(self, session_bus, argv, dbus_name, dbus_path):
        dbus.service.Object.__init__(self, session_bus, dbus_path)

        self.appid, self.game_name, self.width, self.height, self.swf_url = argv
        self.game_name = urllib.unquote(self.game_name)
        self.width = int(self.width)
        self.height = int(self.height)
        self.plug_status = False
        self.conf_db = get_config_file("conf.db")
        self.init_ui()

        def unique(self):
            self.application.window.present()

        def message_receiver(self, *message):
            message_type, contents = message
            if message_type == 'send_plug_id':
                self.content_page.add_plug_id(int(str(contents[1])))
                self.plug_status = True
            elif message_type == 'loading_uri_finish':
                fetch_service.add_missions([self.download_task])

        setattr(Player, 
                'unique', 
                dbus.service.method(dbus_name)(unique))
        setattr(Player, 
                'message_receiver', 
                dbus.service.method(dbus_name)(message_receiver))
        setattr(Player,
                'update_signal',
                dbus.service.signal(dbus_name)(self.update_signal))

        self.send_message('get_plug_id', '')

    def update_signal(self, obj, data=None):
        pass

    def init_ui(self):
        
        self.application = Application()
        self.application.set_default_size(self.width+28, self.height+58)
        self.application.set_skin_preview(get_common_image("frame.png"))
        self.application.set_icon(get_common_image("logo48.png"))
        self.application.add_titlebar(
                ["max","min", "close"],
                )
        player_title = _("Deepin Game Center - %s " % self.game_name)
        self.application.window.set_title(player_title)
        self.application.titlebar.change_name(player_title)

        # Init page box.
        self.page_box = gtk.VBox()
        self.content_page = ContentPage(self.appid)
        self.page_box.add(self.content_page)
        
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

        self.message_label = Label("", enable_gaussian=True)
        label_align = gtk.Alignment()
        label_align.set(0.0, 0.5, 0, 0)
        label_align.set_padding(0, 0, 10, 0)
        label_align.add(self.message_label)
        self.message_box.pack_start(label_align)

        status_box.pack_start(self.message_box, True, True)
        self.statusbar.status_box.pack_start(status_box, True, True)
        self.application.main_box.pack_start(self.statusbar, False, False)

    def start_loading(self):
        self.swf_save_path = os.path.expanduser("~/.cache/deepin-game-center/swf/%s/%s.swf" % (self.appid, self.appid))
        if os.path.exists(self.swf_save_path):
            gtk.timeout_add(200, lambda :self.send_message('load_uri', "file://" + self.swf_save_path))
            self.record_recent_play()
        else:
            touch_file_dir(self.swf_save_path)
            self.load_html_path = os.path.join(static_dir, 'load_swf.html')
            gtk.timeout_add(200, lambda :self.send_message('load_loading_uri', "file://" + self.load_html_path))
            
            self.remote_path = GAME_CENTER_DATA_ADDRESS + self.swf_url
            self.download_task = TaskObject(self.remote_path, self.swf_save_path)
            self.download_task.connect("update", self.download_update)
            self.download_task.connect("finish", self.download_finish)
            self.download_task.connect("error",  self.download_failed)
            self.download_task.connect("start",  self.download_start)

    def run(self):
        self.call_flash_game(self.appid)
        self.start_loading()
        self.application.run()

    def record_recent_play(self):
        if os.path.exists(self.conf_db):
            data = utils.load_db(self.conf_db)
            if self.appid not in data['recent']:
                data['recent'].append(self.appid)
                utils.save_db(data, self.conf_db)
        else:
            data = dict(recent=[self.appid])
            utils.save_db(data, self.conf_db)
        utils.ThreadMethod(utils.send_analytics, ('play', self.appid)).start()

    def call_flash_game(self, local_path):
        flash_frame_path = os.path.join(get_parent_dir(__file__), 'flash_frame.py')
        self.p = subprocess.Popen(['python', flash_frame_path, self.appid], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

    def send_message(self, message_type, contents):
        bus = dbus.SessionBus()
        flash_dbus_name = "com.deepin.game_flash_%s" % (self.appid)
        flash_dbus_path = "/com/deepin/game_flash_%s" % (self.appid)
        if is_dbus_name_exists(flash_dbus_name):
            bus_object = bus.get_object(flash_dbus_name, flash_dbus_path)
            method = bus_object.get_dbus_method("message_receiver")
            method(
                message_type, 
                contents,
                reply_handler=handle_dbus_reply,
                error_handler=handle_dbus_error
            )

    def download_update(self, task, data):
        progress = "%d%%" % data.progress
        self.update_signal(['download_update', progress])

    def download_start(self, task, data):
        pass

    def download_finish(self, task, data):
        self.update_signal(['load_uri', 'file://' + self.swf_save_path])
        self.record_recent_play()

    def download_failed(self, task, data):
        pass

class ContentPage(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self, appid):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)
        self.appid = appid
        self.socket = None
        self.connect("realize", self._add_socket)
        
    def _add_socket(self, w):
        #must create an new socket, because socket will be destroyed when it reparent!!!
        if self.socket:
            self.socket.destroy()
        self.socket = gtk.Socket()
        self.pack_start(self.socket, True, True)
        self.socket.realize()

    def add_plug_id(self, plug_id):
        self._add_socket(None)
        self.socket.add_id(plug_id)
        self.show_all()

    def get_socket_id(self):
        return self.socket.get_id()
                
gobject.type_register(ContentPage)

if __name__ == '__main__':
    import sys

    #sys.argv = sys.argv + ['100000614', '%E8%B7%B3%E8%B7%83%E5%B0%91%E5%A5%B3', '640', '480', '/media/game_media/100000614/100000614.swf']
    DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    appid = sys.argv[1]
    GAME_PLAYER_DBUS_NAME = "com.deepin.game_player_%s" % appid
    GAME_PLAYER_DBUS_PATH = "/com/deepin/game_player_%s" % appid

    if is_dbus_name_exists(GAME_PLAYER_DBUS_NAME, True):
        print "deepin game center has running!"
        
        bus_object = session_bus.get_object(GAME_PLAYER_DBUS_NAME,
                                            GAME_PLAYER_DBUS_PATH)
        #bus_interface = dbus.Interface(bus_object, GAME_PLAYER_DBUS_NAME)
        method = bus_object.get_dbus_method("unique")
        method()

    else:
        # Init dbus.
        bus_name = dbus.service.BusName(GAME_PLAYER_DBUS_NAME, session_bus)
            
        try:
            Player(session_bus, sys.argv[1:], GAME_PLAYER_DBUS_NAME, GAME_PLAYER_DBUS_PATH).run()
        except KeyboardInterrupt:
            pass
