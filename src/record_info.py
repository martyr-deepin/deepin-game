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
import utils

def record_favorite(appid, conf_db):
    if os.path.exists(conf_db):
        data = utils.load_db(conf_db)
        favorite_list = data.get('favorite')
        if favorite_list:
            if appid not in favorite_list:
                data['favorite'].append(appid)
        else:
            data['favorite'] = [appid]
    else:
        data = dict(recent=[appid])

    utils.save_db(data, conf_db)

def remove_favorite(appid, conf_db):
    if os.path.exists(conf_db):
        data = utils.load_db(conf_db)
        if data.get('favorite') and appid in data['favorite']:
            data['favorite'].remove(appid)
            utils.save_db(data, conf_db)

def record_recent_play(appid, conf_db):
    if os.path.exists(conf_db):
        data = utils.load_db(conf_db)
        recent_list = data.get('recent')
        if recent_list:
            if appid not in recent_list:
                data['recent'].append(appid)
        else:
            data['recent'] = [appid]
    else:
        data = dict(recent=[appid])

    utils.save_db(data, conf_db)
    utils.ThreadMethod(utils.send_analytics, ('play', appid)).start()

def remove_recent_play(appid, conf_db):
    if os.path.exists(conf_db):
        data = utils.load_db(conf_db)
        if data.get('recent') and appid in data['favorite']:
            data['favorite'].remove(appid)
            utils.save_db(data, conf_db)
