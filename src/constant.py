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

PROGRAM_NAME = 'deepin-game-center'
PROGRAM_VERSION = '1.0'

GAME_CENTER_DBUS_NAME = 'com.deepin.game_center'
GAME_CENTER_DBUS_PATH = '/com/deepin/game_center' 

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'deepin-game-center')
CACHE_DIR = os.path.join(os.path.expanduser('~'), '.cache', 'deepin-game-center')

COOKIE_FILE = os.path.join(CONFIG_DIR, 'cookie.txt')

DEBUG = False

GAME_CENTER_SERVER_ADDRESS = 'http://game-center.linuxdeepin.com/' if not DEBUG else "http://127.0.0.1:8000/"
GAME_CENTER_DATA_ADDRESS = 'http://game-center.b0.upaiyun.com/' if not DEBUG else "http://127.0.0.1:8000"
