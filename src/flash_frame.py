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

import gtk
import gobject
import glib
from deepin_utils.ipc import is_dbus_name_exists
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import dbus.service
import webkit

class FlashService(dbus.service.Object):
    def __init__(self, 
                 bus_name, 
                 flash_dbus_name, 
                 flash_object_name, 
                 message_handler
                 ):
        # Init dbus object.
        dbus.service.Object.__init__(self, bus_name, flash_object_name)
                
        def wrap_message_handler(self, *a, **kw):
            message_handler(*a, **kw)
        
        # Below code export dbus method dyanmically.
        # Don't use @dbus.service.method !
        setattr(FlashService, 
                'message_receiver', 
                dbus.service.method(flash_dbus_name)(wrap_message_handler))

class FlashFrame(gtk.Plug):
    '''
    class docs
    '''
	
    def __init__(self, appid):
        '''
        init docs
        '''
        # Init.
        gtk.Plug.__init__(self, 0)
        self.appid = appid
        
        # WARING: only use once in one process
        DBusGMainLoop(set_as_default=True) 
        
        # Init threads.
        #gtk.gdk.threads_init()

        # Init dbus.
        self.bus = dbus.SessionBus()
        self.flash_dbus_name = "com.deepin.game_flash_%s" % (self.appid)
        self.flash_object_name = "/com/deepin/game_flash_%s" % (self.appid)
        self.flash_bus_name = dbus.service.BusName(self.flash_dbus_name, bus=self.bus)

        self.webview = webkit.WebView()
        self.add(self.webview)
        
        # Handle signals.
        self.connect("realize", self.flash_frame_realize)
        self.connect("destroy", self.flash_frame_exit)

        glib.timeout_add(1000, self.is_exist)

    def is_exist(self):
        if dbus.SessionBus().name_has_owner("com.deepin.game_player_%s" % self.appid):
            return True
        else:
            glib.timeout_add(0, gtk.main_quit)
            return False

    def run(self):    
        if not hasattr(self, "flash_message_handler"):
            raise Exception, "Please customize your own flash_message_handler for flash_frame"
        
        # Start dbus service.
        FlashService(self.flash_bus_name, 
                      self.flash_dbus_name, 
                      self.flash_object_name,
                      self.flash_message_handler)
        
        # Show.
        self.show_all()
        
        gtk.main()

    def flash_message_handler(self, *message):
        message_type, contents = message
        if message_type == 'exit':
            self.exit()
        elif message_type == 'load_uri':
            self.webview.open(contents)
        elif message_type == 'load_string':
            self.webview.load_string(contents)
        
    def do_delete_event(self, w):
        #a trick to prevent plug destroyed!.  the  better way is recreate an GtkPlug when need reuse it's content
        return True

    def flash_frame_realize(self, widget):
        # Send module information.
        self.send_flash_info()

    def exit(self):
        gtk.main_quit()

    def flash_frame_exit(self, widget):
        print "game %s exit!" % (self.appid)
        
        gtk.main_quit()
        
    def send_message(self, message_type, message_content):
        GAME_PLAYER_DBUS_NAME = "com.deepin.game_player_%s" % self.appid
        GAME_PLAYER_DBUS_PATH = "/com/deepin/game_player_%s" % self.appid
        if is_dbus_name_exists(GAME_PLAYER_DBUS_NAME):
            bus_object = self.bus.get_object(GAME_PLAYER_DBUS_NAME, GAME_PLAYER_DBUS_PATH)
            method = bus_object.get_dbus_method("message_receiver")
            method(message_type, 
                   message_content,
                   reply_handler=self.handle_dbus_reply, # add reply handler
                   error_handler=self.handle_dbus_error  # add error handler
                   )
            
    def handle_dbus_reply(self, *reply):
        # print "%s (reply): %s" % (self.module_dbus_name, str(reply))
        pass
        
    def handle_dbus_error(self, *error):
        #print "%s (error): %s" % (self.module_dbus_name, str(error))
        pass
        
    def send_flash_info(self):
        self.send_message("send_plug_id", (self.appid, self.get_id()))

gobject.type_register(FlashFrame)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        sys.exit(1)
    else:
        FlashFrame(sys.argv[1]).run()
