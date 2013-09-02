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

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from optparse import OptionParser

from deepin_utils.ipc import is_dbus_name_exists

from game_center import GameCenterApp
from player import Player
from constant import (
        GAME_CENTER_DBUS_NAME,
        GAME_CENTER_DBUS_PATH,
        )

def start_main_window():
    DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    
    if is_dbus_name_exists(GAME_CENTER_DBUS_NAME, True):
        print "deepin game center has running!"
        
        bus_object = session_bus.get_object(GAME_CENTER_DBUS_NAME,
                                            GAME_CENTER_DBUS_PATH)
        bus_interface = dbus.Interface(bus_object, GAME_CENTER_DBUS_NAME)
        bus_interface.hello()
        
    else:
        bus_name = dbus.service.BusName(GAME_CENTER_DBUS_NAME, session_bus)
        try:
            GameCenterApp(session_bus).run()
        except KeyboardInterrupt:
            pass

def start_player(args):
    args = args.split(',')
    DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    appid = args[0]
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
        bus_name = dbus.service.BusName(GAME_PLAYER_DBUS_NAME, session_bus)
        try:
            Player(session_bus, args, GAME_PLAYER_DBUS_NAME, GAME_PLAYER_DBUS_PATH).run()
        except KeyboardInterrupt:
            pass

def MainOpionparser():
    parser = OptionParser()
    parser.add_option("-p", "--play", dest="play_game",
            help="infos format: appid,game_name,default_width,default_height,download_path,max_boolean", metavar="infos")
    parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print status messages to stdout")
    (options, args) = parser.parse_args()
    play_game = options.play_game
    if not play_game:
        start_main_window()
    else:
        start_player(options.play_game)

if __name__ == '__main__':
    MainOpionparser()
