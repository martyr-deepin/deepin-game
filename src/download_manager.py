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

from pystorm.services import FetchService
from pystorm.tasks import TaskObject
from constant import GAME_CENTER_DATA_ADDRESS, GAME_CENTER_SERVER_ADDRESS
import os
import json
import threading as td
from deepin_utils.file import touch_file_dir

import urllib2

fetch_service = FetchService(5)
fetch_service.start()

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
        except:
            pass

    def finish_fetch_info(self, index_pic_url):
        pic_url = "%s/%s" % (GAME_CENTER_DATA_ADDRESS, index_pic_url)
        pic_local_path = os.path.join(os.path.dirname(self.desc_info_path), pic_url.split('/')[-1])
        if not os.path.exists(pic_local_path):
            fetch_service.add_missions([TaskObject(pic_url, pic_local_path)])
