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

import sys
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from theme import app_theme
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.application import Application
from utils import get_common_image

from constant import (
        GAME_CENTER_DBUS_NAME,
        GAME_CENTER_DBUS_PATH,
        )
from nls import _

class GameCenterApp(dbus.service.Object):

    def __init__(self, session_bus):
        dbus.service.Object.__init__(self, session_bus, GAME_CENTER_DBUS_PATH)

        self.init_ui()

    def init_ui(self):
        self.application = Application(resizable=False)
        self.application.set_default_size(888, 634)
        self.application.set_skin_preview(get_common_image("frame.png"))
        self.application.set_icon(get_common_image("logo48.png"))
        self.application.add_titlebar(
                ["theme", "menu", "max","min", "close"],
                show_title=False
                )
        self.application.window.set_title(_("Deepin Game Center"))

        self.application.run()

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
            GameCenterApp(session_bus)
        except KeyboardInterrupt:
            pass

