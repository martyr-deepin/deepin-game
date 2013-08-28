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

import cookielib
from constant import COOKIE_FILE, GAME_CENTER_SERVER_ADDRESS

def get_cookie_star(appid):
    domain = GAME_CENTER_SERVER_ADDRESS.split('/')[2].split(':')[0]
    path = '/game/details/%s' % appid
    m = cookielib.MozillaCookieJar()
    m.load(COOKIE_FILE)
    c = m._cookies
    if domain not in c:
        return None
    else:
        c2 = c[domain]
        if path not in c2:
            return None
        else:
            c3 = c2[path]
            _cookie = c3.get('star')
            if _cookie:
                return _cookie.value
            else:
                return None
