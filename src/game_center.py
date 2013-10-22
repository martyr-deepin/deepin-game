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
import jswebkit
import urlparse
import urllib

from theme import app_theme
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.utils import get_widget_root_coordinate
from dtk.ui.constant import WIDGET_POS_BOTTOM_LEFT
from dtk.ui.menu import Menu
from dtk.ui.application import Application
from dtk.ui.statusbar import Statusbar
from dtk.ui.theme import DynamicPixbuf
from dtk.ui.browser import WebView
from dtk.ui.skin_config import skin_config
from dtk.ui.slider import Wizard
from deepin_utils.file import get_parent_dir

from dialog import AboutDialog
from paned_box import PanedBox
from widgets import BottomTipBar
from navigatebar import Navigatebar
from animation import favorite_animation
from utils import get_common_image
import utils
import record_info
from xdg_support import get_config_file
from download_manager import FetchInfo
from nls import _, LANGUAGE
from events import global_event
from constant import (
        GAME_CENTER_DBUS_NAME,
        GAME_CENTER_DBUS_PATH,
        GAME_CENTER_SERVER_ADDRESS,
        CACHE_DIR,
        COOKIE_FILE,
        )

static_dir = os.path.join(get_parent_dir(__file__, 2), "static")


class GameCenterApp(dbus.service.Object):

    def __init__(self, session_bus):
        dbus.service.Object.__init__(self, session_bus, GAME_CENTER_DBUS_PATH)
        self.conf_db = get_config_file("conf.db")

        self.init_ui()

    def init_ui(self):
        self.application = Application()
        self.application.set_default_size(1082, 666)
        self.application.set_skin_preview(get_common_image("frame.png"))
        self.application.set_icon(get_common_image("logo48.png"))
        self.application.add_titlebar(
                ["theme", "menu", "max","min", "close"],
                show_title=False
                )
        self.application.window.set_title(_("Deepin Games"))

        # Init page box.
        self.page_box = gtk.VBox()
        
        # Init page align.
        self.page_align = gtk.Alignment()
        self.page_align.set(0.5, 0.5, 1, 1)
        self.page_align.set_padding(0, 0, 2, 2)
        
        # Append page to switcher.
        self.paned_box = PanedBox(24)
        self.paned_box.add_content_widget(self.page_box)
        self.bottom_tip_bar = BottomTipBar()
        self.bottom_tip_bar.close_button.connect('clicked', lambda w: self.paned_box.bottom_window.hide())
        self.paned_box.add_bottom_widget(self.bottom_tip_bar)

        self.page_align.add(self.paned_box)
        self.application.main_box.pack_start(self.page_align, True, True)
        
        # Init status bar.
        self.statusbar = Statusbar(30)
        status_box = gtk.HBox()

        self.statusbar.status_box.pack_start(status_box, True, True)
        self.application.main_box.pack_start(self.statusbar, False, False)

        self.webview = WebView(COOKIE_FILE)
        webkit.set_web_database_directory_path(CACHE_DIR)
        web_settings = self.webview.get_settings()
        web_settings.set_property("enable-page-cache", True)
        web_settings.set_property("enable-offline-web-application-cache", True)
        #web_settings.set_property("enable-file-access-from-file-uris", True)
        web_settings.set_property('enable-universal-access-from-file-uris', True)
        web_settings.set_property("enable-default-context-menu", False)
        self.webview.set_settings(web_settings)
        #self.webview.enable_inspector()
        self.webview.connect('new-window-policy-decision-requested', self.navigation_policy_decision_requested_cb)
        #self.webview.connect('notify::load-status', self.webview_load_status_handler)
        self.webview.connect('notify::title', self.webview_title_changed_handler)
        self.webview.connect('script-alert', self.webview_script_alert_handler)
        self.webview.connect('window-object-cleared', self.webview_window_object_cleared)
        #self.webview.connect('load-progress-changed', self.load_progress)
        
        self.home_url = urllib.basejoin(GAME_CENTER_SERVER_ADDRESS, 'game/?hl=%s' % LANGUAGE)
        self.webview.load_uri(self.home_url)

        self.page_box.add(self.webview)
        
        self.navigatebar = Navigatebar(
                [
                (None, _("Home"), self.show_home_page),
                (None, _("Topics"), self.show_subject_page),
                (None, _("My Games"), self.show_mygame_page),
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

        self.about_dialog = AboutDialog(_('About us'))
        self.about_dialog.set_transient_for(self.application.window)

        # Init menu.
        #if LANGUAGE == 'en_US':
            #menu_min_width = 185
        #else:
            #menu_min_width = 150

        menu = Menu(
            [
             (None, _("Clear all cached data"), self.clean_download_cache),
             (None, _("See what's new"), lambda : self.show_wizard_win()),
             (None, _("About us"), self.show_about_dialog),
             (None, _("Quit"), lambda: gtk.main_quit()),
             ],
            is_root_menu=True,
            #menu_min_width=menu_min_width,
            )
        self.application.set_menu_callback(
            lambda button:
                menu.show(
                get_widget_root_coordinate(button, WIDGET_POS_BOTTOM_LEFT),
                (button.get_allocation().width, 0)))
        
        self.no_favorite_html_path = os.path.join(static_dir, "error-no-favorite.html")
        self.no_recent_html_path = os.path.join(static_dir, "error-no-recent.html")
        self.mygame_frame_path = os.path.join(static_dir, "mygame-frame.html")
        self.gallery_html_path = os.path.join(static_dir, 'game-mygame.html')

        skin_config.connect('theme-changed', self.theme_changed_handler)
        global_event.register_event('show-message', self.update_message)

    def load_progress(self, webview, progress):
        print progress

    def webview_window_object_cleared(self, webview, frame, context, window_object):
        ctx = jswebkit.JSContext(frame.get_global_context())
        window = ctx.EvaluateScript("window")
        window.css_color = skin_config.theme_name
        location = window.location.href
        parse_result = urlparse.urlparse(location)

        frame.get_web_view().execute_script('var global_l18n_str = %s' % json.dumps({
                'my_favorites': _('My favorites'),
                'my_recent': _('My recents'),
                },
                encoding='UTF-8',
                ensure_ascii=False,
                ))
        frame.get_web_view().execute_script('var global_language = %s' %
                json.dumps(LANGUAGE, encoding='UTF-8', ensure_ascii=False))

        if parse_result.path == self.no_favorite_html_path or parse_result.path == self.no_recent_html_path:
            window.css_language = LANGUAGE

    def update_message(self, message, hide_timeout=0):
        if not self.paned_box.bottom_window.is_visible():
            self.paned_box.bottom_window.show()
        if isinstance(message, list) and len(message) == 3:
            self.bottom_tip_bar.update_info(*message)
        else:
            self.bottom_tip_bar.update_info(message)
        if hide_timeout != 0:
            gtk.timeout_add(hide_timeout, lambda:self.paned_box.bottom_window.hide())
    
    def ready_show(self):    
        if not utils.is_wizard_showed():
            self.show_wizard_win(True, callback=self.wizard_callback)
            utils.set_wizard_showed()
        else:    
            self.application.window.show_all()
        gtk.main()

    def show_wizard_win(self, show_button=False, callback=None):    

        lang = LANGUAGE
            
        Wizard(
            [get_common_image('wizard/%s/%s.png' % (lang, i)) for i in range(3)],
            (
                get_common_image('wizard/dot_normal.png'), 
                get_common_image('wizard/dot_active.png'),
            ),
            (
                get_common_image('wizard/%s/start_normal.png' % lang), 
                get_common_image('wizard/%s/start_press.png' % lang), 
            ),
            show_button,
            callback
            ).show_all()
        
    def wizard_callback(self):
        self.application.window.show_all()
        gtk.timeout_add(100, self.application.raise_to_top)

    def clean_download_cache(self):
        info = {
                'file_num':0,
                'total_size':0
                }
        downloads_dir = os.path.join(CACHE_DIR, 'downloads')
        appids =  os.listdir(downloads_dir)
        for appid in appids:
            files = os.listdir(os.path.join(downloads_dir, appid))
            for f in files:
                if f.endswith('.swf'):
                    swf_path = os.path.join(downloads_dir, appid, f)
                    info['file_num'] += 1
                    info['total_size'] += os.path.getsize(swf_path)
                    os.remove(os.path.join(downloads_dir, appid, f))
        
        if info['file_num']:
            cache_cleaned_message = _('%s files are deleted and %s disk space is freed.') % (
                    info['file_num'], utils.get_human_size(info['total_size']))
        else:
            cache_cleaned_message = _('Your game cache is empty.')
        global_event.emit('show-message', cache_cleaned_message, 5000)

    def show_about_dialog(self):
        self.about_dialog.show_all()

    def theme_changed_handler(self, widget, name):
        self.webview.execute_script('change_color_theme(%s)' %
            json.dumps(name, encoding="UTF-8", ensure_ascii=False))
        self.webview.execute_script('$("#game-gallery").get(0).contentWindow.change_color_theme(%s)' %
            json.dumps(name, encoding="UTF-8", ensure_ascii=False))
        self.webview.execute_script('alert("scroll_top://" + $($("#game-gallery").get(0).contentWindow.document.body).scrollTop())')

    def send_event(self, data=0):
        press_event = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        press_event.window = self.webview.window
        press_event.x = 1062.0
        press_event.y = 35.0 + int(data) + 20.0
        press_event.button = 1

        release_event = gtk.gdk.Event(gtk.gdk.BUTTON_RELEASE)
        release_event.window = self.webview.window
        release_event.x = 1062.0
        release_event.y = 35.0 + int(data) + 20.0
        release_event.button = 1

        self.webview.event(press_event)
        self.webview.event(release_event)
        self.webview.window.invalidate_rect(self.webview.allocation, True)

    def webview_message_handler(self, info):
        info = info.split('://')
        if len(info) == 2:
            order, data = info

            if order == 'play':
                self.show_play(data)

            elif order == 'star':
                self.toggle_favorite(data)

            elif order == 'local':
                if data == 'recent':
                    self.show_recent_page()
                elif data == 'star':
                    self.show_favorite_page()

            elif order == 'document_ready' and data == 'game_gallery':
                self.document_ready()
                
            elif order == 'onload' and data == 'game_gallery':
                gtk.timeout_add(200, self.fresh_favotite_status)

            elif order == 'onload' and data == 'local_game_gallery':
                self.webview.execute_script('$("#game-gallery").get(0).contentWindow.set_right_menu()')
                gtk.timeout_add(200, self.fresh_favotite_status)

            elif order == 'onload' and data == 'main_frame':
                gtk.timeout_add(200, self.show_favorite_page)

            elif order == 'onload' and data == 'footer':
                self.webview.execute_script('if(infos){append_data_to_gallery(infos);}')

            elif order == 'favorite':
                record_info.record_favorite(data, self.conf_db)
                FetchInfo(data).start()
                favorite_animation(self.application.window)

            elif order == 'unfavorite':
                record_info.remove_favorite(data, self.conf_db)

            elif order == 'local_action':
                info = data.split('-')
                if len(info) == 2:
                    action_type= info[0]
                    appid = info[1]
                    if action_type == 'favorite':
                        record_info.remove_favorite(appid, self.conf_db)
                        utils.ThreadMethod(utils.send_analytics, ('unfavorite', appid)).start()
                        #var favorite_url = 'http://' + location.host + '/game/analytics/?type=unfavorite&appid=' + id;
                        self.webview.execute_script('if(infos){infos_remove(%s);}else{gallery_change(%s);}' % (
                                json.dumps(appid, encoding="UTF-8", ensure_ascii=False),
                                json.dumps(self.no_favorite_html_path, encoding="UTF-8", ensure_ascii=False),
                                ))
                    elif action_type == 'recent':
                        record_info.remove_recent_play(appid, self.conf_db)
                        self.webview.execute_script('if(infos){infos_remove(%s);}else{gallery_change(%s);}' % (
                                json.dumps(appid, encoding="UTF-8", ensure_ascii=False),
                                json.dumps(self.no_recent_html_path, encoding="UTF-8", ensure_ascii=False),
                                ))

            elif order == 'scroll_top':
                self.send_event(data)

    def navigation_policy_decision_requested_cb(self, web_view, frame, request, navigation_action, policy_decision):
        uri = request.get_uri()
        if uri.startswith('http://') or uri.startswith('https://'):
            return False
        else:
            self.webview_message_handler(uri)
            return True

    def webview_script_alert_handler(self, widget, frame, uri, data=None):
        self.webview_message_handler(uri)
        return True

    def webview_title_changed_handler(self, webview, data=None):
        title = webview.get_title()
        if title:
            self.webview_message_handler(title)

    def fresh_favotite_status(self):
        if os.path.exists(self.conf_db):
            data = utils.load_db(self.conf_db)
            if data.get('favorite'):
                for id in data['favorite']:
                    self.webview.execute_script("change_favorite_status(%s, 'ilike')" %
                        json.dumps(id, encoding="UTF-8", ensure_ascii=False))

    def webview_load_status_handler(self, widget=None, status=None):
        load_status = widget.get_load_status()
        if load_status == webkit.LOAD_FINISHED:
            self.webview.execute_script("$('#game-gallery').contents().find('#grid span span').removeClass('ilike')")
            self.webview.execute_script("$('#game-gallery').contents().find('#grid span span').addClass('like')")

    def document_ready(self):
        self.webview.execute_script("$('#game-gallery').contents().find('#grid span span').removeClass('ilike')")
        self.webview.execute_script("$('#game-gallery').contents().find('#grid span span').addClass('like')")

    def show_play(self, data):
        data = data.split(',')
        player_path = os.path.join(get_parent_dir(__file__), 'deepin-game-center.py')
        order = ['python', player_path]
        order.append('-p')
        order.append(','.join(data))
        self.p = subprocess.Popen(order, stderr=subprocess.STDOUT, shell=False)

    #def mute_handler(self, widget, data=None):
        #active = widget.get_active()
        #current_sink = pypulse.get_fallback_sink_index()
        #if current_sink is not None:
            #pypulse.PULSE.set_output_mute(current_sink, active)

    def print_info(self, info_type, info):
        if info:
            print info_type, info

    def toggle_favorite(self, data):
        print "toggle favorite"

    def show_home_page(self):
        self.webview.load_uri(self.home_url)

    def show_subject_page(self):
        self.subject_url = urllib.basejoin(GAME_CENTER_SERVER_ADDRESS, 'game/subjects/?hl=%s' % LANGUAGE)
        self.webview.load_uri(self.subject_url)

    def show_mygame_page(self):
        self.webview.open('file://' + self.mygame_frame_path)
        
    def show_favorite_page(self):
        downloads_dir = os.path.join(CACHE_DIR, 'downloads')
        if os.path.exists(self.conf_db):
            data = utils.load_db(self.conf_db)
            if data.get('favorite'):
                infos = []
                favorite_list = data['favorite']
                for id in favorite_list:
                    try:
                        info_js_path = os.path.join(downloads_dir, str(id), 'info.json')
                        info = json.load(open(info_js_path))
                        info['index_pic_url'] = os.path.join(downloads_dir, str(id), info['index_pic_url'].split('/')[-1])
                        #info['swf_game'] = os.path.join(downloads_dir, str(id), info['swf_game'].split('/')[-1])
                        info['swf_game'] = urlparse.urlparse(info['swf_game']).path[1:]
                        info['type'] = 'favorite'
                        infos.append(info)
                    except Exception, e:
                        print "Load favorite page error:", e
                if infos:
                    self.webview.execute_script('var infos=%s' % 
                            json.dumps(infos, encoding="UTF-8", ensure_ascii=False))
                    self.webview.execute_script("gallery_change(%s)" %
                            json.dumps(self.gallery_html_path, encoding="UTF-8", ensure_ascii=False))
                    return

        self.webview.execute_script("gallery_change(%s)" %
                json.dumps(self.no_favorite_html_path, encoding="UTF-8", ensure_ascii=False))

    def show_recent_page(self):
        downloads_dir = os.path.join(CACHE_DIR, 'downloads')
        if os.path.exists(self.conf_db):
            data = utils.load_db(self.conf_db)
            if data.get('recent'):
                infos = []
                recent_list = data['recent']
                for id in recent_list:
                    try:
                        info_js_path = os.path.join(downloads_dir, str(id), 'info.json')
                        info = json.load(open(info_js_path))
                        info['index_pic_url'] = os.path.join(downloads_dir, str(id), info['index_pic_url'].split('/')[-1])
                        #info['swf_game'] = os.path.join(downloads_dir, str(id), info['swf_game'].split('/')[-1])
                        info['swf_game'] = urlparse.urlparse(info['swf_game']).path[1:]
                        info['type'] = 'recent'
                        infos.append(info)
                    except:
                        pass
                if infos:
                    self.webview.execute_script('var infos=%s' % 
                            json.dumps(infos, encoding="UTF-8", ensure_ascii=False))
                    self.webview.execute_script("gallery_change(%s)" %
                        json.dumps(self.gallery_html_path, encoding="UTF-8", ensure_ascii=False))
                    return

        self.webview.execute_script("gallery_change(%s)" %
                json.dumps(self.no_recent_html_path, encoding="UTF-8", ensure_ascii=False))

    def run(self):
        self.ready_show()

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
