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
import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import subprocess
import json
import webkit

from theme import app_theme
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.application import Application
from dtk.ui.statusbar import Statusbar
from dtk.ui.theme import DynamicPixbuf
from dtk.ui.browser import WebView 
from deepin_utils.file import get_parent_dir, touch_file_dir

from navigatebar import Navigatebar
from button import ToggleButton
from utils import get_common_image
import utils
import record_info
from xdg_support import get_config_file
import pypulse_small as pypulse
from sound_manager import SoundSetting
from download_manager import FetchInfo
from nls import _
from constant import (
        GAME_CENTER_DBUS_NAME,
        GAME_CENTER_DBUS_PATH,
        GAME_CENTER_SERVER_ADDRESS,
        CACHE_DIR,
        )

static_dir = os.path.join(get_parent_dir(__file__, 2), "static")

class GameCenterApp(dbus.service.Object):

    def __init__(self, session_bus):
        dbus.service.Object.__init__(self, session_bus, GAME_CENTER_DBUS_PATH)
        self.conf_db = get_config_file("conf.db")
        self.sound_manager = SoundSetting()

        self.init_ui()
        self.sound_manager.connect('mute-state', lambda w, b: self.mute_button.set_active(b))

    def init_ui(self):
        self.application = Application()
        self.application.set_default_size(1060, 660)
        self.application.set_skin_preview(get_common_image("frame.png"))
        self.application.set_icon(get_common_image("logo48.png"))
        self.application.add_titlebar(
                ["theme", "menu", "max","min", "close"],
                show_title=False
                )
        self.application.window.set_title(_("深度游戏中心"))

        # Init page box.
        self.page_box = gtk.VBox()
        
        # Init page align.
        self.page_align = gtk.Alignment()
        self.page_align.set(0.5, 0.5, 1, 1)
        self.page_align.set_padding(0, 0, 2, 2)
        
        # Append page to switcher.
        self.page_align.add(self.page_box)
        self.application.main_box.pack_start(self.page_align, True, True)
        
        # Init status bar.
        self.statusbar = Statusbar(24)
        status_box = gtk.HBox()

        mute_on_dpixbuf = DynamicPixbuf(utils.get_common_image('function/mute_on.png'))
        mute_off_dpixbuf = DynamicPixbuf(utils.get_common_image('function/mute_off.png'))
        self.mute_button = ToggleButton(
                mute_off_dpixbuf, mute_on_dpixbuf, 
                button_label='静音', label_color='#ffffff',
                padding_x=5)
        self.mute_button.connect('clicked', self.mute_handler)
        mute_button_align = gtk.Alignment()
        mute_button_align.set(1, 0.5, 0, 0)
        mute_button_align.set_padding(4, 4, 5, 30)
        mute_button_align.add(self.mute_button)

        status_box.pack_end(mute_button_align, False, False)

        self.statusbar.status_box.pack_start(status_box, True, True)
        self.application.main_box.pack_start(self.statusbar, False, False)

        self.webview = WebView(os.path.join(CACHE_DIR, 'cookie.txt'))
        web_settings = self.webview.get_settings()
        web_settings.set_property("enable-file-access-from-file-uris", True)
        self.webview.set_settings(web_settings)
        self.webview.enable_inspector()
        self.webview.connect('new-window-policy-decision-requested', self.navigation_policy_decision_requested_cb)
        self.webview.connect('notify::load-status', self.webview_load_status_handler)
        self.webview.connect('script-alert', self.webview_script_alert_handler)
        
        self.webview.load_uri(GAME_CENTER_SERVER_ADDRESS+'game')

        self.page_box.add(self.webview)
        
        self.navigatebar = Navigatebar(
                [
                (None, _("首页"), self.show_home_page),
                (None, _("游戏专题"), self.show_subject_page),
                (None, _("我的游戏"), self.show_mygame_page),
                ],
                font_size = 11,
                padding_x = 5,
                padding_y = 16,
                vertical=False,
                item_normal_pixbuf=DynamicPixbuf(get_common_image('top/nav_normal.png')),
                item_hover_pixbuf=DynamicPixbuf(get_common_image('top/nav_hover.png')),
                item_press_pixbuf=DynamicPixbuf(get_common_image('top/nav_press.png')),
                )
        self.navigatebar.set_size_request(-1, 56)
        self.navigatebar_align = gtk.Alignment(0, 0, 1, 1)
        self.navigatebar_align.set_padding(0, 0, 4, 0)
        self.navigatebar_align.add(self.navigatebar)
        self.application.titlebar.set_size_request(-1, 56)
        self.application.titlebar.left_box.pack_start(self.navigatebar_align, True, True)
        self.application.window.add_move_event(self.navigatebar)

    def webview_script_alert_handler(self, widget, frame, uri, data=None):
        info = uri.split('://')
        if len(info) == 2:
            order, data = uri.split('://')
            if order == 'play':
                self.show_play(data)
            elif order == 'star':
                self.toggle_favorite(data)
            elif order == 'local':
                if data == 'recent':
                    self.show_recent_page()
                elif data == 'star':
                    self.show_favorite_page()
            elif order == 'onload' and data == 'game_gallery':
                gtk.timeout_add(200, self.fresh_favotite_status)
            elif order == 'onload' and data == 'main_frame':
                gtk.timeout_add(200, self.show_favorite_page)
            elif order == 'onload' and data == 'footer':
                self.webview.execute_script('if(infos){append_data_to_gallery(infos);}')
            elif order == 'favorite':
                record_info.record_favorite(data, self.conf_db)
                FetchInfo(data).start()
            elif order == 'unfavorite':
                record_info.remove_favorite(data, self.conf_db)
        return True

    def fresh_favotite_status(self):
        if os.path.exists(self.conf_db):
            data = utils.load_db(self.conf_db)
            if data.get('favorite'):
                for id in data['favorite']:
                    self.webview.execute_script("change_favorite_status(%s, 'ilike')" %
                        json.dumps(id, encoding="UTF-8", ensure_ascii=False))

    def webview_load_status_handler(self, widget, status,):
        load_status = widget.get_load_status()
        if load_status == webkit.LOAD_FINISHED:
            self.webview.execute_script("$('#game-gallery').contents().find('#grid span span').removeClass('ilike')")
            self.webview.execute_script("$('#game-gallery').contents().find('#grid span span').addClass('like')")

    def navigation_policy_decision_requested_cb(self, web_view, frame, request, navigation_action, policy_decision):
        uri = request.get_uri()
        if uri.startswith('http://') or uri.startswith('https://'):
            return False
        else:
            self.uri_handle(uri)
            return True

    def uri_handle(self, uri):
        order, data = uri.split('://')
        if order == 'play':
            self.show_play(data)
        elif order == 'star':
            self.toggle_favorite(data)
        elif order == 'local':
            if data == 'recent':
                self.show_recent_page()
            elif data == 'star':
                self.show_favorite_page()

    def show_play(self, data):
        data = data.split(',')
        player_path = os.path.join(get_parent_dir(__file__), 'player.py')
        order = ['python', player_path]
        for info in data:
            order.append(info.strip())
        error_log = '/tmp/deepin-game-center/game-%s.log' % data[1]
        touch_file_dir(error_log)
        with open(error_log, 'wb') as error_fp:
            self.p = subprocess.Popen(order, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=error_fp, shell=False)

    def mute_handler(self, widget, data=None):
        active = widget.get_active()
        current_sink = pypulse.get_fallback_sink_index()
        if current_sink is not None:
            pypulse.PULSE.set_output_mute(current_sink, active)

    def print_info(self, info_type, info):
        if info:
            print info_type, info

    def toggle_favorite(self, data):
        print "toggle favorite"

    def show_home_page(self):
        self.webview.load_uri(GAME_CENTER_SERVER_ADDRESS+'game')

    def show_subject_page(self):
        pass

    def show_mygame_page(self):
        self.gallery_html_path = os.path.join(static_dir, 'game-gallery.html')
        main_frame_path = os.path.join(static_dir, "main-frame.html")
        self.webview.open('file://' + main_frame_path)
        
    def show_favorite_page(self):
        downloads_dir = os.path.join(CACHE_DIR, 'downloads')
        if os.path.exists(self.conf_db):
            data = utils.load_db(self.conf_db)
            if data.get('favorite'):
                infos = []
                for id in data['favorite']:
                    try:
                        info_js_path = os.path.join(downloads_dir, str(id), 'info.json')
                        info = json.load(open(info_js_path))
                        info['index_pic_url'] = os.path.join(downloads_dir, str(id), info['index_pic_url'].split('/')[-1])
                        info['swf_game'] = os.path.join(downloads_dir, str(id), info['swf_game'].split('/')[-1])
                        infos.append(info)
                    except:
                        pass
                self.webview.execute_script('var infos=%s' % 
                        json.dumps(infos, encoding="UTF-8", ensure_ascii=False))
                self.webview.execute_script("gallery_change(%s)" %
                        json.dumps(self.gallery_html_path, encoding="UTF-8", ensure_ascii=False))
                return

        no_favorite_html_path = os.path.join(static_dir, "error-no-favorite.html")
        self.webview.execute_script("gallery_change(%s)" %
                json.dumps(no_favorite_html_path, encoding="UTF-8", ensure_ascii=False))

    def show_recent_page(self):
        downloads_dir = os.path.join(CACHE_DIR, 'downloads')
        if os.path.exists(self.conf_db):
            data = utils.load_db(self.conf_db)
            if data.get('recent'):
                infos = []
                for id in data['recent']:
                    try:
                        info_js_path = os.path.join(downloads_dir, str(id), 'info.json')
                        info = json.load(open(info_js_path))
                        info['index_pic_url'] = os.path.join(downloads_dir, str(id), info['index_pic_url'].split('/')[-1])
                        info['swf_game'] = os.path.join(downloads_dir, str(id), info['swf_game'].split('/')[-1])
                        infos.append(info)
                    except:
                        pass
                self.webview.execute_script('var infos=%s' % 
                        json.dumps(infos, encoding="UTF-8", ensure_ascii=False))
                self.webview.execute_script("gallery_change(%s)" %
                    json.dumps(self.gallery_html_path, encoding="UTF-8", ensure_ascii=False))
                return

        no_recent_html_path = os.path.join(static_dir, "error-no-recent.html")
        self.webview.execute_script("gallery_change(%s)" %
                json.dumps(no_recent_html_path, encoding="UTF-8", ensure_ascii=False))

    def run(self):
        self.application.run()

    @dbus.service.method(GAME_CENTER_DBUS_NAME, in_signature="", out_signature="")    
    def hello(self):
        self.application.window.present()

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
            GameCenterApp(session_bus).run()
        except KeyboardInterrupt:
            pass
