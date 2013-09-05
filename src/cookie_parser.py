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
import cookielib
import time

from deepin_utils.file import touch_file
from constant import COOKIE_FILE, GAME_CENTER_SERVER_ADDRESS

ONE_DAY_SECONDS = 60*60*24

def get_cookie_star(appid):
    domain = GAME_CENTER_SERVER_ADDRESS.split('/')[2].split(':')[0]
    path = '/game/details/%s' % appid
    m = cookielib.MozillaCookieJar()
    try:
        m.load(COOKIE_FILE)
    except Exception, e:
        print e
        return None
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
                return _cookie
            else:
                return None

def set_cookie_star(appid, star):
    domain = GAME_CENTER_SERVER_ADDRESS.split('/')[2].split(':')[0]
    path = '/game/details/%s' % appid
    m = cookielib.MozillaCookieJar()
    try:
        m.load(COOKIE_FILE)
    except:
        pass

    expires = int(time.time() + ONE_DAY_SECONDS)
    c = cookielib.Cookie(
            version=0, 
            name='star', 
            value=str(star), 
            port=None, 
            port_specified=False, 
            domain=domain, 
            domain_specified=False, 
            domain_initial_dot=False, 
            path=path, 
            path_specified=False, 
            secure=False, 
            expires=expires, 
            discard=False, 
            comment=None, 
            comment_url=None, 
            rest={}, 
            rfc2109=False,
            )

    m.set_cookie(c)
    if not os.path.exists(COOKIE_FILE):
        touch_file(COOKIE_FILE)
    m.save(COOKIE_FILE)

if __name__ == '__main__':
    #cookie = set_cookie_star(3362, 10)
    print get_cookie_star(3506)
