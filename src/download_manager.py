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
import traceback

import logging
logging.basicConfig(level=logging.ERROR)
from pystorm.services import FetchService
from pystorm.tasks import TaskObject
from constant import GAME_CENTER_DATA_ADDRESS, GAME_CENTER_SERVER_ADDRESS
import os
import json
import threading as td
from deepin_utils.file import touch_file_dir
from events import global_event

import urllib
import urllib2

fetch_service = FetchService(1)
fetch_service.start()

class FetchSwf(td.Thread):
    def __init__(self, ):
        td.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        pass

class SetStarScore(td.Thread):
    def __init__(self, appid, star):
        td.Thread.__init__(self)
        self.daemon = True
        self.appid = appid
        self.star = star

    def run(self):
        url = "%sgame/analytics/?type=star&appid=%s&mark=%s" % (GAME_CENTER_SERVER_ADDRESS, self.appid, self.star)
        try:
            js = urllib2.urlopen(url).read()
            if js:
                js = json.loads(js)
                if js['status'] == 'OK':
                    global_event.emit('set-star-score-success', js)
                else:
                    print "Star error"
                    print js
        except Exception, e:
            print 'SetStarScore Error:', e

class FetchInfo(td.Thread):
    def __init__(self, appid):
        td.Thread.__init__(self)
        self.daemon = True
        self.appid = appid
        self.desc_info_path = os.path.expanduser("~/.cache/deepin-game-center/downloads/%s/info.json" % self.appid)
        touch_file_dir(self.desc_info_path)

    def run(self):
        self.download_json_info(self.appid)

    def download_json_info(self, appid):
        info_json_url = "%sgame/info/%s" % (GAME_CENTER_SERVER_ADDRESS, appid)
        try:
            js = urllib2.urlopen(info_json_url).read()
            if js:
                info = json.loads(js)
                json.dump(info, open(self.desc_info_path, 'wb'))
                self.finish_fetch_info(info['index_pic_url'])
                global_event.emit('download-app-info-finish', json.dumps(info))
        except Exception, e:
            traceback.print_exc(sys.stdout)
            print "Error msg:",e
            if os.path.exists(self.desc_info_path):
                info = json.load(open(self.desc_info_path))
                global_event.emit('download-app-info-finish', json.dumps(info))

    def finish_fetch_info(self, index_pic_url):
        pic_url = urllib.basejoin(GAME_CENTER_DATA_ADDRESS, index_pic_url)
        pic_local_path = os.path.join(os.path.dirname(self.desc_info_path), pic_url.split('/')[-1])
        if not os.path.exists(pic_local_path):
            try:
                pic_str = urllib2.urlopen(pic_url).read()
                with open(pic_local_path, 'wb') as fp:
                    fp.write(pic_str) 
            except Exception, e:
                print "Fetch index picture faild:", e
