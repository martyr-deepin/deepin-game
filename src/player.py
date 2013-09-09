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
import gobject
import cairo
import subprocess
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import urllib
import json
import copy

from theme import app_theme
from application import PlayerApplication
from titlebar import Titlebar
#import pypulse_small as pypulse
from guide_box import GuideBox
from paned_box import PanedBox
from control_toolbar import ControlToolbar
from utils import get_common_image, handle_dbus_reply, handle_dbus_error
import record_info
from nls import _
from constant import GAME_CENTER_DATA_ADDRESS
from download_manager import fetch_service, FetchInfo
from xdg_support import get_config_file
#from sound_manager import SoundSetting
from constant import PROGRAM_NAME
from events import global_event
import utils

from dtk.ui.utils import alpha_color_hex_to_cairo, container_remove_all, propagate_expose
from dtk.ui.skin_config import skin_config
from dtk.ui.draw import draw_pixbuf
from dtk.ui.constant import DEFAULT_FONT_SIZE
from deepin_utils.file import get_parent_dir, touch_file_dir
from deepin_utils.ipc import is_dbus_name_exists
from dtk.ui.draw import draw_pixbuf, draw_text, draw_round_rectangle

info_data = os.path.join(get_parent_dir(__file__, 2), "data", "info.db")
static_dir = os.path.join(get_parent_dir(__file__, 2), "static")

class Player(dbus.service.Object):
    def __init__(self, session_bus, argv, dbus_name, dbus_path):
        dbus.service.Object.__init__(self, session_bus, dbus_path)

        self.appid, self.game_name, self.width, self.height, self.swf_url, self.resizable = argv
        self.game_name = urllib.unquote(self.game_name)
        self.width = int(self.width)
        self.height = int(self.height)
        self.plug_status = False
        self.conf_db = get_config_file("conf.db")
        self.p = None
        self.current_sink_index = None
        #self.sound_manager = SoundSetting(self.sound_sink_callback)
        self.loading = True
        self.hand_pause = False
        self.game_pause = False
        self.fullscreen_state = False
        self.guide_box_expand = True
        self.window_normal_info = {}
        self.maximize_state = False

        self.call_flash_game(self.appid)
        self.init_ui()
        self.plug_id = None

        def unique(self):
            self.application.window.present()

        def message_receiver(self, *message):
            message_type, contents = message
            if message_type == 'send_plug_id':
                self.plug_id = int(str(contents[1]))
                self.content_page.add_plug_id(self.plug_id)
                self.plug_status = True
                self.start_loading()
            elif message_type == 'loading_uri_finish':
                fetch_service.add_missions([self.download_task])
            elif message_type == 'enter_bottom':
                if self.show_bottom:
                    self.paned_box.bottom_window.show()
            elif message_type == 'enter_top':
                if self.show_top:
                    self.paned_box.top_window.show()
            elif message_type == 'onload_loading':
                self.start_download_swf()
            elif message_type == 'game_action':
                if contents == 'pause':
                    self.command_pause_game()

        setattr(Player, 
                'unique', 
                dbus.service.method(dbus_name)(unique))
        setattr(Player, 
                'message_receiver', 
                dbus.service.method(dbus_name)(message_receiver))
        setattr(Player,
                'update_signal',
                dbus.service.signal(dbus_name)(self.update_signal))

        self.send_message('get_plug_id', '')

    def sound_sink_callback(self, dt, index):
        sound_id = int(dt['proplist']['application.process.id'])
        if self.p and sound_id == self.p.pid:
            self.current_sink_index = index

    def update_signal(self, obj, data=None):
        pass

    def init_ui(self):
        
        self.application = PlayerApplication(close_callback=self.quit, max_callback=self.max_callback)
        if self.width+12 < 642:
            width = 642 + 220
        else:
            width = self.width + 12 + 220
        self.application.set_default_size(width, self.height+73)
        self.application.set_skin_preview(get_common_image("frame.png"))
        self.application.set_icon(get_common_image("logo48.png"))
        self.application.add_titlebar(
                ["mode", "min", "max", "close"],
                )
        player_title = _("Deepin Games - %s ") % self.game_name
        self.window = self.application.window
        self.window.set_title(player_title)
        self.application.titlebar.change_name(player_title)
        self.application.titlebar.mode_button.set_active(True)
        self.application.titlebar.mode_button.connect('toggled', self.change_view)
        self.application.titlebar.close_button.connect('clicked', self.quit)
        #self.application.window.connect('focus-out-event', self.window_out_focus_hander)
        self.application.window.connect('focus-in-event', self.window_in_focus_hander)
        self.application.window.connect('window-state-event', self.window_state_change_handler)
        self.application.window.connect('key-press-event', self.window_key_press_handler)

        self.page_box = gtk.HBox()
        self.content_page = ContentPage(self.appid)
        self.content_page.screenshot_box.connect('button-press-event', self.external_continue_action)

        self.guide_box = GuideBox()
        self.guide_box.set_size_request(220, -1)
        
        self.page_align = gtk.Alignment()
        self.page_align.set(0.5, 0.5, 1, 1)
        self.page_align.set_padding(0, 0, 2, 2)
        
        self.control_toolbar = self.create_toolbar()
        self.page_box.pack_start(self.content_page)
        self.page_box.pack_start(self.guide_box, False)

        self.inner_top_titlebar = self.create_top_titlebar()
        self.inner_top_titlebar.change_name(player_title)
        self.inner_control_toolbar = self.create_toolbar()

        self.paned_box = PanedBox()
        self.paned_box.add_content_widget(self.page_box)
        self.paned_box.add_bottom_widget(self.inner_control_toolbar)
        self.paned_box.add_top_widget(self.inner_top_titlebar)

        self.page_align.add(self.paned_box)
        self.application.main_box.pack_start(self.page_align)
        self.application.window.add_move_event(self.control_toolbar)
        self.show_bottom = False
        self.display_normal()

    def window_key_press_handler(self, widget, event):
        if self.fullscreen_state:
            from dtk.ui.keymap import get_keyevent_name
            if get_keyevent_name(event, True) == 'Escape':
                self.control_toolbar.fullscreen_button.clicked()

    def create_top_titlebar(self,
                     button_mask=['min', "close"],
                     icon_path=None, 
                     app_name=None, 
                     title=None, 
                     add_separator=False, 
                     show_title=True, 
                     enable_gaussian=True, 
                     name_size=DEFAULT_FONT_SIZE,
                     title_size=DEFAULT_FONT_SIZE,
                     ):
        titlebar = Titlebar(
                    button_mask, 
                    icon_path, 
                    app_name, 
                    title, 
                    add_separator, 
                    show_title=show_title, 
                    enable_gaussian=enable_gaussian,
                    name_size=name_size,
                    title_size=title_size,
                    )
        if "min" in button_mask:
            titlebar.min_button.connect("clicked", lambda w: self.window.min_window())
        if "close" in button_mask:
            titlebar.close_button.connect("clicked", self.quit)

        return titlebar

    def create_toolbar(self):
        control_toolbar = ControlToolbar(self.appid)
        control_toolbar.mute_button.connect('clicked', self.mute_handler)
        control_toolbar.pause_button.connect('button-press-event', self.pause_handler)
        control_toolbar.replay_button.connect('clicked', self.replay_action)
        control_toolbar.fullscreen_button.connect('clicked', self.fullscreen_handler)
        control_toolbar.share_button.connect('clicked', self.share_action)
        control_toolbar.favorite_button.connect('button-release-event', self.favorite_action)
        control_toolbar.leave_callback = self.leave_callback
        
        if os.path.exists(self.conf_db):
            data = utils.load_db(self.conf_db)
            if data.get('favorite') and self.appid in data['favorite']:
                control_toolbar.favorite_button.set_active(True)

        return control_toolbar

    def favorite_action(self, widget, event):
        if not widget.get_active():
            record_info.record_favorite(self.appid, self.conf_db)
        else:
            record_info.remove_favorite(self.appid, self.conf_db)

    def leave_callback(self, widget, e):
        if self.fullscreen_state:
            if e.window == self.paned_box.bottom_window:
                self.paned_box.bottom_window.hide()
            elif e.window == self.paned_box.top_window:
                self.paned_box.top_window.hide()

    def window_state_change_handler(self, widget, event):
        if event.new_window_state == gtk.gdk.WINDOW_STATE_ICONIFIED:
            self.external_pause_action()

    def external_pause_action(self):
        if not self.loading and (not self.hand_pause and not self.game_pause):
            self.control_toolbar.pause_button.set_active(True)
            self.toggle_pause_action(self.control_toolbar.pause_button)

    def external_continue_action(self, widget=None, event=None):
        if not self.loading and self.game_pause:
            self.control_toolbar.pause_button.set_active(False)
            self.toggle_pause_action(self.control_toolbar.pause_button)

    def window_in_focus_hander(self, widget, event):
        #print "In: hand=>%s, pause=>%s" % (self.hand_pause, self.game_pause)
        if not self.loading and (not self.hand_pause and self.game_pause):
            self.control_toolbar.pause_button.set_active(False)
            self.toggle_pause_action(self.control_toolbar.pause_button)

    def window_out_focus_hander(self, widget, event):
        #print "Out: hand=>%s, pause=>%s" % (self.hand_pause, self.game_pause)
        min_state = self.window.get_state() == gtk.gdk.WINDOW_STATE_ICONIFIED
        if not self.loading and (not self.hand_pause and not self.game_pause) and min_state:
            self.control_toolbar.pause_button.set_active(True)
            self.toggle_pause_action(self.control_toolbar.pause_button)

    def change_view(self, widget):
        screen = gtk.gdk.screen_get_default()
        screen_w, screen_h = screen.get_width(), screen.get_height()
        width, height = self.window.get_size()

        DEFAULT_HEIGHT = height

        if not widget.get_active():
            self.guide_box_expand = False
            DEFAULT_WIDTH = width - 220
            self.guide_box.hide_all()
            self.guide_box.set_no_show_all(True)


        else:
            self.guide_box_expand = True
            DEFAULT_WIDTH = width + 220
            self.guide_box.set_no_show_all(False)
            self.guide_box.show_all()

        if self.maximize_state:
            DEFAULT_WIDTH = screen_w

        self.window.set_default_size(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.window.set_geometry_hints(None, DEFAULT_WIDTH, DEFAULT_HEIGHT, 
                                        screen_w, screen_h,  -1, -1, -1, -1, -1, -1)
        self.window.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)

    def max_callback(self, widget):
        screen = gtk.gdk.screen_get_default()
        screen_w, screen_h = screen.get_width(), screen.get_height()

        window_state = self.window.window.get_state()
        if window_state & gtk.gdk.WINDOW_STATE_MAXIMIZED == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            self.maximize_state = False
            self.window.unmaximize()

            if self.window_normal_info['guide_box_expand'] == self.guide_box_expand:
                width, height = self.window_normal_info['width'], self.window_normal_info['height']
            else:
                if self.window_normal_info['guide_box_expand']:
                    p_width, p_height = self.window_normal_info['width'], self.window_normal_info['height']
                    width = p_width - 220
                    height = p_height
                else:
                    p_width, p_height = self.window_normal_info['width'], self.window_normal_info['height']
                    width = p_width + 220
                    height = p_height

            self.window.set_geometry_hints(None, width, height, 
                                        screen_w, screen_h,  -1, -1, -1, -1, -1, -1)
            self.window.resize(width, height)

        else:
            self.maximize_state = True
            self.window_normal_info['guide_box_expand'] = copy.deepcopy(self.guide_box_expand)
            self.window_normal_info['width'] = copy.deepcopy(self.window.get_size()[0])
            self.window_normal_info['height'] = copy.deepcopy(self.window.get_size()[1])
            self.window.maximize()

    def quit(self, widget, data=None):
        if self.game_pause:
            os.system('kill -9 %s' % self.p.pid)
        gtk.main_quit()

    def display_normal(self):
        self.application.show_titlebar()
        self.guide_box.show_all()
        self.application.main_box.pack_start(self.control_toolbar, False, False)
        self.application.window.show_window()
        if getattr(self.paned_box, "bottom_window"):
            self.paned_box.bottom_window.hide()
        if getattr(self.paned_box, 'top_window'):
            self.paned_box.top_window.hide()

    def fullscreen_handler(self, widget, data=None):
        self.control_toolbar.fullscreen_button.set_state(gtk.STATE_NORMAL)
        self.inner_control_toolbar.fullscreen_button.set_state(gtk.STATE_NORMAL)
        if self.fullscreen_state:
            self.fullscreen_state = False
            self.display_normal()
            self.show_bottom = False
            self.show_top = False
            self.page_align.set_padding(0, 0, 2, 2)
            self.application.window.unfullscreen()
        else:
            self.fullscreen_state = True
            # for fullscreen mode
            self.paned_box.connect('leave-notify-event', self.leave_callback)
            self.paned_box.paint_bottom_window = self.__paint_bottom_toolbar_background
            self.paned_box.paint_top_window = self.__paint_top_titlebar_background
            self.show_bottom = True
            self.show_top = True

            self.application.hide_titlebar()
            self.application.main_box.remove(self.control_toolbar)
            self.control_toolbar.show_all()
            self.application.window.show_window()
            self.guide_box.hide_all()
            self.page_align.set_padding(0, 0, 0, 0)
            self.application.window.fullscreen()

    def mute_handler(self, widget, data=None):
        #if self.current_sink_index:
            #pypulse.PULSE.set_sink_input_mute(self.current_sink_index, widget.get_active())
        pass

    def replay_action(self, widget, data=None):
        if self.game_pause:
            self.control_toolbar.pause_button.set_active(False)
            self.toggle_pause_action(self.control_toolbar.pause_button)
        if not self.loading:
            self.update_signal(['load_uri', 'file://%s,%s,%s' % (self.swf_save_path, self.width, self.height)])

    def toggle_pause_action(self, widget):
        if widget.get_active():
            self.update_signal(['game_action', 'pause'])
        else:
            self.command_continue_game()
        self.game_pause = widget.get_active() 

    def content_socket_press_handler(self, widget, event):
        print event

    def pause_handler(self, widget, data=None):
        if not widget.get_active():
            self.update_signal(['game_action', 'pause'])
            self.hand_pause = True
        else:
            self.command_continue_game()
            self.hand_pause = False
        self.game_pause = not widget.get_active() 

    def command_pause_game(self):
        screenshot_pixbuf = self.get_game_screenshot_pixbuf()
        self.content_page.remove_socket(screenshot_pixbuf)
        os.system('kill -STOP %s' % self.p.pid)

    def command_continue_game(self):
        os.system('kill -CONT %s' % self.p.pid)
        self.content_page.add_plug_id(self.plug_id)
        #self.update_signal(['game_action', 'continue'])

    def fullscreen_action(self, widget, data=None):
        pass

    def get_game_screenshot_pixbuf(self):

        rect = self.content_page.get_allocation()
        #rect = self.window.get_allocation()
        width = rect.width
        height = rect.height
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
        pixbuf = pixbuf.get_from_drawable(self.content_page.window, self.content_page.window.get_colormap(), 
                                            rect.x, rect.y, 0, 0, width, height)
        return pixbuf

    def share_action(self, widget, data=None):
        #from window import get_screenshot_pixbuf
        #pixbuf = get_screenshot_pixbuf(False)

        #rect = self.content_page.get_allocation()
        rect = self.window.get_allocation()
        width = rect.width
        height = rect.height
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
        pixbuf = pixbuf.get_from_drawable(self.window.window, self.window.get_colormap(), 
                                            rect.x, rect.y, 0, 0, width, height)

        filename = self.save_to_tmp_file(pixbuf)
        share_path = os.path.join(get_parent_dir(__file__), 'share.py')
        
        self.share_p = subprocess.Popen(['python', share_path, filename], stderr=subprocess.STDOUT, shell=False)
        self.external_pause_action()

    def save_to_tmp_file(self, pixbuf):
        from tempfile import mkstemp
        import os
        tmp = mkstemp(".tmp", PROGRAM_NAME)
        os.close(tmp[0])
        filename = tmp[1]
        pixbuf.save(filename, "jpeg", {"quality":"100"})
        return filename

    def start_loading(self):
        global_event.register_event('download-app-info-finish', self.app_info_download_finish)
        FetchInfo(self.appid).start()
        self.swf_save_path = os.path.expanduser("~/.cache/deepin-game-center/downloads/%s/%s.swf" % (self.appid, self.appid))
        if os.path.exists(self.swf_save_path):
            gtk.timeout_add(200, lambda:self.load_game())
        else:
            gtk.timeout_add(200, self.show_loading_page)
            
            
    def show_loading_page(self):
        touch_file_dir(self.swf_save_path)
        self.load_html_path = os.path.join(static_dir, 'loading.html')
        self.send_message('load_loading_uri', 'file://' + self.load_html_path)

    def start_download_swf(self):
        self.remote_path = urllib.basejoin(GAME_CENTER_DATA_ADDRESS, self.swf_url)
        utils.ThreadMethod(urllib.urlretrieve, (self.remote_path, self.swf_save_path + '_tmp', self.report_hook)).start()

        #self.download_task = TaskObject(self.remote_path, self.swf_save_path, verbose=True)
        #self.download_task.connect("update", self.download_update)
        #self.download_task.connect("finish", self.download_finish)
        #self.download_task.connect("error",  self.download_failed)
        #self.download_task.connect("start",  self.download_start)

    def report_hook(self, block_count, block_size, total_size):
        current = block_count * block_size
        if current < total_size:
            percent = str(int(float(current)/total_size * 100))
            self.update_signal(['download_update', percent])
        else:
            self.update_signal(['download_update', '100'])
            os.system('mv %s %s' % (self.swf_save_path + '_tmp', self.swf_save_path))
            self.load_game()
            #gtk.timeout_add(500, lambda:self.load_game())

    def load_game(self):
        self.loading = False
        self.update_signal(['download_finish', 'file://%s,%s,%s' % (self.swf_save_path, self.width, self.height)])
        record_info.record_recent_play(self.appid, self.conf_db)

        #self.loading = False
        #self.send_message('load_uri', 'file://%s,%s,%s' % (self.swf_save_path, self.width, self.height))
        #record_info.record_recent_play(self.appid, self.conf_db)
            
    def run(self):
        self.application.window.show_window()
        #self.paned_box.bottom_window.set_composited(True)
        gtk.main()

    def app_info_download_finish(self, js):
        gtk.timeout_add(500, self.import_infos, js)

    def import_infos(self, infos):
        if not self.loading:
            self.send_message('app_info_download_finish', json.dumps(infos))
            return False
        return True

    def call_flash_game(self, local_path):
        flash_frame_path = os.path.join(get_parent_dir(__file__), 'flash_frame.py')
        self.p = subprocess.Popen(['python', flash_frame_path, self.appid], stderr=subprocess.STDOUT, shell=False)

    def send_message(self, message_type, contents):
        bus = dbus.SessionBus()
        flash_dbus_name = "com.deepin.game_flash_%s" % (self.appid)
        flash_dbus_path = "/com/deepin/game_flash_%s" % (self.appid)
        if is_dbus_name_exists(flash_dbus_name):
            bus_object = bus.get_object(flash_dbus_name, flash_dbus_path)
            method = bus_object.get_dbus_method("message_receiver")
            method(
                message_type, 
                contents,
                reply_handler=handle_dbus_reply,
                error_handler=handle_dbus_error
            )

    def download_update(self, task, data):
        #print "%s/s" % utils.get_human_size(data.speed)
        progress = "%d" % data.progress
        self.update_signal(['download_update', progress])

    def download_start(self, task, data):
        pass

    def download_finish(self, task, data):
        gtk.timeout_add(500, lambda:self.load_game())

    def download_failed(self, task, data):
        pass

    def __paint_bottom_toolbar_background(self, e):
        # 将皮肤的图片画在bottom toolbar上,作为背景.
        cr = e.window.cairo_create()
        bottom_size = e.window.get_size()
        # draw background.
        cr.set_source_rgba(*alpha_color_hex_to_cairo(("#ebebeb", 0.1)))
        cr.rectangle(0, 0, bottom_size[0], bottom_size[1])
        cr.fill()
        # draw background pixbuf.
        pixbuf = skin_config.background_pixbuf
        app_h = self.application.window.allocation.height
        app_w = self.application.window.allocation.width
        bottom_h = bottom_size[1]
        # 当图片的高度小雨窗口高度的时候,只拿出图片的最尾巴.
        if pixbuf.get_height() > app_h + bottom_h:
            h = app_h
        else:
            h = pixbuf.get_height() - bottom_h
        # 当图片小于窗口宽度的时候,拉伸图片.
        if pixbuf.get_width() < app_w:
            pixbuf = pixbuf.scale_simple(app_w,
                                pixbuf.get_width(),
                                gtk.gdk.INTERP_BILINEAR)

        draw_pixbuf(cr, 
                    pixbuf, 
                    0, 
                    -(h))

    def __paint_top_titlebar_background(self, e):
        # 将皮肤的图片画在bottom toolbar上,作为背景.
        cr = e.window.cairo_create()
        bottom_size = e.window.get_size()
        # draw background.
        cr.set_source_rgba(*alpha_color_hex_to_cairo(("#ebebeb", 0.1)))
        cr.rectangle(0, 0, bottom_size[0], bottom_size[1])
        cr.fill()
        # draw background pixbuf.
        pixbuf = skin_config.background_pixbuf
        app_w = self.application.window.allocation.width
        # 当图片小于窗口宽度的时候,拉伸图片.
        if pixbuf.get_width() < app_w:
            pixbuf = pixbuf.scale_simple(app_w,
                                pixbuf.get_width(),
                                gtk.gdk.INTERP_BILINEAR)

        draw_pixbuf(cr, 
                    pixbuf, 
                    0, 
                    0)

class ContentPage(gtk.VBox):
    '''
    class docs
    '''
	
    def __init__(self, appid):
        '''
        init docs
        '''
        gtk.VBox.__init__(self)
        self.appid = appid
        self.socket = None

        self.socket_box = gtk.EventBox()
        self.socket_box.connect("realize", self._add_socket)

        self.screenshot_box = gtk.EventBox()
        self.screenshot_box.connect('expose-event', self.screenshot_box_expose)

        #self.pack_start(self.socket_box, True, True)
        #self.pack_start(self.screenshot_box, True, True)

        self.screenshot_pixbuf = None

    def screenshot_box_expose(self, widget, event):
        rect = widget.allocation
        cr = widget.window.cairo_create()

        #cr.set_source_rgba(1.0, 1.0, 1.0, 0.0) 
        #cr.set_operator(cairo.OPERATOR_SOURCE)
        #cr.paint()
        
        if self.screenshot_pixbuf:
            draw_pixbuf(cr, self.screenshot_pixbuf, rect.x, rect.y)

        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(*rect)
        cr.fill()

        if widget.state == gtk.STATE_PRELIGHT:
            play_pixbuf = utils.get_common_image_pixbuf('pause/play_hover.png')
        else:
            play_pixbuf = utils.get_common_image_pixbuf('pause/play_normal.png')

        draw_pixbuf(
                cr, 
                play_pixbuf, 
                rect.x + (rect.width - play_pixbuf.get_width())/2,
                rect.y + (rect.height - play_pixbuf.get_height())/2,
                )

        # Propagate expose to children.
        propagate_expose(widget, event)

        return True

    def _add_socket(self, w):
        #must create an new socket, because socket will be destroyed when it reparent!!!
        if self.socket:
            self.socket.destroy()
        self.socket = gtk.Socket()
        self.socket_box.add(self.socket)
        self.socket.realize()

    def remove_socket(self, pixbuf=None):
        if pixbuf:
            self.screenshot_pixbuf = pixbuf
            self.screenshot_box.queue_draw()
        self.socket.destroy()

        container_remove_all(self)
        self.pack_start(self.screenshot_box, True, True)
        self.show_all()

    def add_plug_id(self, plug_id):
        if self.screenshot_box in self.get_children():
            self.remove(self.screenshot_box)
        self.pack_start(self.socket_box, True, True)
        self._add_socket(None)
        self.socket.add_id(plug_id)
        self.show_all()

    def get_socket_id(self):
        return self.socket.get_id()
                
gobject.type_register(ContentPage)


if __name__ == '__main__':
    import sys

    #sys.argv = sys.argv + ['100000614', '%E8%B7%B3%E8%B7%83%E5%B0%91%E5%A5%B3', '640', '480', '/media/game_media/100000614/100000614.swf']
    DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    appid = sys.argv[1]
    GAME_PLAYER_DBUS_NAME = "com.deepin.game_player_%s" % appid
    GAME_PLAYER_DBUS_PATH = "/com/deepin/game_player_%s" % appid

    if is_dbus_name_exists(GAME_PLAYER_DBUS_NAME, True):
        print "deepin game center has running!"
        
        bus_object = session_bus.get_object(GAME_PLAYER_DBUS_NAME,
                                            GAME_PLAYER_DBUS_PATH)
        #bus_interface = dbus.Interface(bus_object, GAME_PLAYER_DBUS_NAME)
        method = bus_object.get_dbus_method("unique")
        method()

    else:
        # Init dbus.
        bus_name = dbus.service.BusName(GAME_PLAYER_DBUS_NAME, session_bus)
            
        try:
            Player(session_bus, sys.argv[1:], GAME_PLAYER_DBUS_NAME, GAME_PLAYER_DBUS_PATH).run()
        except KeyboardInterrupt:
            pass
