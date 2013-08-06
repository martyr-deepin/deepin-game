#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import gtk
import gobject
import subprocess

from theme import app_theme
from dtk.ui.application import Application
from dtk.ui.statusbar import Statusbar
from dtk.ui.label import Label
from deepin_utils.file import get_parent_dir
from utils import get_common_image, handle_dbus_reply, handle_dbus_error
from nls import _
from constant import GAME_CENTER_SERVER_ADDRESS

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from deepin_utils.ipc import is_dbus_name_exists

info_data = os.path.join(get_parent_dir(__file__, 2), "data", "info.db")
static_dir = os.path.join(get_parent_dir(__file__, 2), "static")

def get_game_info(appid):
    conn = sqlite3.connect(info_data)
    cursor = conn.cursor()
    cursor.execute("select name, width, height from gameapp where appid=?", [int(appid), ])
    return cursor.fetchone()

class Player(dbus.service.Object):
    def __init__(self, session_bus, appid, dbus_name, dbus_path):
        dbus.service.Object.__init__(self, session_bus, dbus_path)

        self.appid = appid
        self.init_ui()

        def unique(self):
            self.application.window.present()

        def message_receiver(self, *message):
            message_type, contents = message
            if message_type == 'send_plug_id':
                self.content_page.add_plug_id(int(str(contents[1])))

        setattr(Player, 
                'unique', 
                dbus.service.method(dbus_name)(unique))
        setattr(Player, 
                'message_receiver', 
                dbus.service.method(dbus_name)(message_receiver))

    def init_ui(self):
        game_name, width, height = get_game_info(self.appid)
        
        self.application = Application()
        self.application.set_default_size(width + 10, height + 10)
        self.application.set_skin_preview(get_common_image("frame.png"))
        self.application.set_icon(get_common_image("logo48.png"))
        self.application.add_titlebar(
                ["theme", "menu", "max","min", "close"],
                )
        self.application.window.set_title(_("Deepin Game Center - %s " % game_name))
        self.application.titlebar.change_name(_("Deepin Game Center - %s " % game_name))

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
        else:
            info_path = GAME_CENTER_SERVER_ADDRESS + "game/info/" + str(appid)
            print info_path
            load_html_path = os.path.join(static_dir, 'load_swf.html')
            gtk.timeout_add(200, lambda :self.send_message('load_uri', "file://" + load_html_path))

    def run(self):
        self.call_flash_game(self.appid)
        self.start_loading()
        self.application.run()

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
                
gobject.type_register(ContentPage)

if __name__ == '__main__':
    import sys
    sys.argv.append('100000600')

    if len(sys.argv) != 2:
        print sys.argv
        sys.exit(1)
    else:
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
                Player(session_bus, appid, GAME_PLAYER_DBUS_NAME, GAME_PLAYER_DBUS_PATH).run()
            except KeyboardInterrupt:
                pass
