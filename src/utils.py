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
import cPickle
import shutil
import fcntl
import threading as td
import urllib, urllib2
from constant import GAME_CENTER_SERVER_ADDRESS

LOG_PATH = "/tmp/dgc-frontend.log"

dgc_root_dir = os.path.realpath(get_parent_dir(__file__, 2))

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
    pass
    
def handle_dbus_error(obj, error=None):
    #global_logger.logerror("Dbus Reply Error: %s", obj)
    #global_logger.logerror("ERROR MESSAGE: %s", error)
    pass

def load_db(fn):    
    '''Load object from db file.'''
    objs = None
    if os.path.exists(fn):
        f = open(fn, "rb")
        try:
            objs = cPickle.load(f)
        except:    
            print "%s is not a valid database.", fn
            try:
                shutil.copy(fn, fn + ".not-valid")
            except: pass    
            objs = None
        f.close()    
    return objs    

def save_db(objs, fn):
    '''Save object to db file.'''
    f = open(fn + ".tmp", "w")
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    cPickle.dump(objs, f, cPickle.HIGHEST_PROTOCOL)
    f.close()
    os.rename(fn + ".tmp", fn)

class ThreadMethod(td.Thread):
    '''
    func: a method name
    args: arguments tuple
    '''
    def __init__(self, func, args, daemon=True):
        td.Thread.__init__(self)
        self.func = func
        self.args = args
        self.setDaemon(daemon)

    def run(self):
        self.func(*self.args)

def send_analytics(analytics_type, appid):
    url = GAME_CENTER_SERVER_ADDRESS + "game/analytics/"
    data = dict(
            type=analytics_type,
            appid=appid
            )
    req_url = "%s?%s" % (url, urllib.urlencode(data))
    urllib2.urlopen(req_url)

