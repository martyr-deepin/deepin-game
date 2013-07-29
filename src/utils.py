#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011~2012 Deepin, Inc.
#               2011~2012 Kaisheng Ye
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

from datetime import datetime
import os
from deepin_utils.file import get_parent_dir
import gtk
from logger import newLogger

LOG_PATH = "/tmp/dgc-frontend.log"

dgc_root_dir = os.path.realpath(get_parent_dir(__file__, 2))

global_logger = newLogger('global')

def get_common_image(name):
    return os.path.join(dgc_root_dir, "image", name)

def get_common_image_pixbuf(name):
    if os.path.exists(get_common_image(name)):
        return gtk.gdk.pixbuf_new_from_file(get_common_image(name))
    else:
        return None

def write_log(message):
    if not os.path.exists(LOG_PATH):
        open(LOG_PATH, "w").close()
        os.chmod(LOG_PATH, 0777)
    with open(LOG_PATH, "a") as file_handler:
        now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        file_handler.write("%s %s\n" % (now, message))

def handle_dbus_reply(obj=None):
    global_logger.loginfo("Dbus Reply OK: %s", obj)
    
def handle_dbus_error(obj, error=None):
    global_logger.logerror("Dbus Reply Error: %s", obj)
    global_logger.logerror("ERROR MESSAGE: %s", error)

