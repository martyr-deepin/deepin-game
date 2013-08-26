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
import subprocess
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import urllib

from theme import app_theme
from application import PlayerApplication
from dtk.ui.utils import alpha_color_hex_to_cairo, container_remove_all
from dtk.ui.skin_config import skin_config
from dtk.ui.draw import draw_pixbuf
from deepin_utils.file import get_parent_dir, touch_file_dir
from deepin_utils.ipc import is_dbus_name_exists

import pypulse_small as pypulse
from guide_box import GuideBox
from paned_box import PanedBox
from control_toolbar import ControlToolbar
from utils import get_common_image, handle_dbus_reply, handle_dbus_error
import record_info
from nls import _
from constant import GAME_CENTER_DATA_ADDRESS
from download_manager import fetch_service, TaskObject, FetchInfo
from xdg_support import get_config_file
from sound_manager import SoundSetting
from constant import PROGRAM_NAME

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
        self.sound_manager = SoundSetting(self.sound_sink_callback)
        self.loading = True
        self.hand_pause = False
        self.game_pause = False
        self.fullscreen_state = False
        self.init_ui()

        def unique(self):
            self.application.window.present()

        def message_receiver(self, *message):
            message_type, contents = message
            if message_type == 'send_plug_id':
                self.content_page.add_plug_id(int(str(contents[1])))
                self.plug_status = True
            elif message_type == 'loading_uri_finish':
                fetch_service.add_missions([self.download_task])
            elif message_type == 'enter_bottom':
                self.paned_box.bottom_window.show()

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
        
        self.application = PlayerApplication(close_callback=self.quit)
        self.application.set_default_size(self.width+26+220, self.height+75)
        self.application.set_skin_preview(get_common_image("frame.png"))
        self.application.set_icon(get_common_image("logo48.png"))
        self.application.add_titlebar(
                ["theme", "mode", "min","close"],
                )
        player_title = _("深度游戏中心 - %s " % self.game_name)
        self.window = self.application.window
        self.window.set_title(player_title)
        self.application.titlebar.change_name(player_title)
        self.application.titlebar.mode_button.set_active(True)
        self.application.titlebar.mode_button.connect('toggled', self.change_view)
        self.application.titlebar.close_button.connect('clicked', self.quit)
        self.application.window.connect('focus-out-event', self.window_out_focus_hander)
        self.application.window.connect('focus-in-event', self.window_in_focus_hander)

        self.page_box = gtk.HBox()
        self.content_page = ContentPage(self.appid)

        self.guide_box = GuideBox()
        self.guide_box.set_size_request(220, -1)
        
        self.page_align = gtk.Alignment()
        self.page_align.set(0.5, 0.5, 1, 1)
        self.page_align.set_padding(0, 0, 2, 2)
        
        self.control_toolbar = ControlToolbar()
        self.control_toolbar.mute_button.connect('clicked', self.mute_handler)
        self.control_toolbar.pause_button.connect('button-press-event', self.pause_handler)
        self.control_toolbar.replay_button.connect('clicked', self.replay_action)
        self.control_toolbar.fullscreen_button.connect('clicked', self.fullscreen_handler)
        self.control_toolbar.share_button.connect('clicked', self.share_action)
        self.control_toolbar.leave_callback = self.leave_callback


        self.page_box.pack_start(self.content_page)
        self.page_box.pack_start(self.guide_box, False)
        self.page_align.add(self.page_box)
        self.paned_box = PanedBox()
        self.paned_box.add_content_widget(self.page_align)
        self.application.main_box.pack_start(self.paned_box)
        self.display_normal()

    def leave_callback(self, widget, e):
        if self.fullscreen_state and e.window == self.paned_box.bottom_window:
            self.paned_box.bottom_window.hide()

    def window_in_focus_hander(self, widget, event):
        print "In: hand=>%s, pause=>%s" % (self.hand_pause, self.game_pause)
        if not self.loading and (not self.hand_pause and self.game_pause):
            self.control_toolbar.pause_button.set_active(False)
            self.toggle_pause_action(self.control_toolbar.pause_button)

    def window_out_focus_hander(self, widget, event):
        print "Out: hand=>%s, pause=>%s" % (self.hand_pause, self.game_pause)
        if not self.loading and (not self.hand_pause and not self.game_pause):
            self.control_toolbar.pause_button.set_active(True)
            self.toggle_pause_action(self.control_toolbar.pause_button)

    def change_view(self, widget):
        width, height = self.window.get_size()
        if not widget.get_active():
            SIMPLE_DEFAULT_WIDTH = width - 220
            SIMPLE_DEFAULT_HEIGHT = height
            #self.window.unmaximize()
            self.guide_box.hide_all()
            self.guide_box.set_no_show_all(True)
            self.window.set_default_size(SIMPLE_DEFAULT_WIDTH, SIMPLE_DEFAULT_HEIGHT)
            self.window.set_geometry_hints(None, SIMPLE_DEFAULT_WIDTH, SIMPLE_DEFAULT_HEIGHT, 
                                           SIMPLE_DEFAULT_WIDTH, SIMPLE_DEFAULT_HEIGHT, # (310, 700)
                                           -1, -1, -1, -1, -1, -1)
            self.window.resize(SIMPLE_DEFAULT_WIDTH, SIMPLE_DEFAULT_HEIGHT)
            self.window.queue_draw()
        else:
            FULL_DEFAULT_WIDTH = width + 220
            FULL_DEFAULT_HEIGHT = height
            self.guide_box.set_no_show_all(False)
            self.guide_box.show_all()
            self.window.set_default_size(FULL_DEFAULT_WIDTH, FULL_DEFAULT_HEIGHT)            
            self.window.set_geometry_hints(None, FULL_DEFAULT_WIDTH, FULL_DEFAULT_HEIGHT, 
                                           FULL_DEFAULT_WIDTH, FULL_DEFAULT_HEIGHT,  -1, -1, -1, -1, -1, -1)
            self.window.resize(FULL_DEFAULT_WIDTH, FULL_DEFAULT_HEIGHT)

    def quit(self, widget, data=None):
        os.system('kill -9 %s' % self.p.pid)
        self.application.window.close_window()

    def display_normal(self):
        self.application.show_titlebar()
        self.guide_box.show_all()
        self.application.main_box.pack_start(self.control_toolbar, False, False)
        self.application.window.show_window()

    def fullscreen_handler(self, widget, data=None):
        window_state = self.application.window.get_state()
        if window_state == gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.fullscreen_state = False
            self.display_normal()
        else:

            self.fullscreen_state = True
            # for fullscreen mode
            self.paned_box.connect('leave-notify-event', self.leave_callback)
            self.paned_box.paint_bottom_window = self.__paint_bottom_toolbar_background

            #container_remove_all(self.application.main_box)
            self.application.main_box.remove(self.page_align)
            self.application.main_box.remove(self.control_toolbar)
            #container_remove_all(self.page_box)
            self.page_box.remove(self.content_page)
            self.page_box.remove(self.guide_box)
            #container_remove_all(self.page_align)
            self.page_align.remove(self.page_box)

            self.application.hide_titlebar()
            self.paned_box.add_content_widget(self.content_page)
            self.paned_box.add_bottom_widget(self.control_toolbar)
            self.application.main_box.pack_start(self.paned_box)
            self.application.window.show_window()

    def mute_handler(self, widget, data=None):
        if self.current_sink_index:
            pypulse.PULSE.set_sink_input_mute(self.current_sink_index, widget.get_active())

    def replay_action(self, widget, data=None):
        if not self.loading:
            self.update_signal(['load_uri', 'file://' + self.swf_save_path])

    def toggle_pause_action(self, widget):
        if widget.get_active():
            os.system('kill -STOP %s' % self.p.pid)
        else:
            os.system('kill -CONT %s' % self.p.pid)
        self.game_pause = widget.get_active() 

    def pause_handler(self, widget, data=None):
        if not widget.get_active():
            os.system('kill -STOP %s' % self.p.pid)
            self.hand_pause = True
        else:
            os.system('kill -CONT %s' % self.p.pid)
            self.hand_pause = False
        self.game_pause = not widget.get_active() 

    def fullscreen_action(self, widget, data=None):
        pass

    def share_action(self, widget, data=None):
        #from window import get_screenshot_pixbuf
        #pixbuf = get_screenshot_pixbuf(False)

        rect = self.content_page.get_allocation()
        width = rect.width
        height = rect.height
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
        pixbuf = pixbuf.get_from_drawable(self.content_page.window, self.content_page.get_colormap(), 
                                            rect.x, rect.y, 0, 0, width, height)

        filename = self.save_to_tmp_file(pixbuf)
        share_path = os.path.join(get_parent_dir(__file__), 'share.py')
        
        subprocess.Popen(['python', share_path, filename], stderr=subprocess.STDOUT, shell=False)

    def save_to_tmp_file(self, pixbuf):
        from tempfile import mkstemp
        import os
        tmp = mkstemp(".tmp", PROGRAM_NAME)
        os.close(tmp[0])
        filename = tmp[1]
        pixbuf.save(filename, "jpeg", {"quality":"100"})
        return filename

    def start_loading(self):
        FetchInfo(self.appid).start()
        self.swf_save_path = os.path.expanduser("~/.cache/deepin-game-center/downloads/%s/%s.swf" % (self.appid, self.appid))
        if os.path.exists(self.swf_save_path):
            gtk.timeout_add(500, lambda:self.load_game())
        else:
            touch_file_dir(self.swf_save_path)
            self.load_html_path = os.path.join(static_dir, 'loading.html')
            gtk.timeout_add(500, lambda :self.send_message('load_loading_uri', "file://" + self.load_html_path))
            
            self.remote_path = GAME_CENTER_DATA_ADDRESS + self.swf_url
            self.download_task = TaskObject(self.remote_path, self.swf_save_path)
            self.download_task.connect("update", self.download_update)
            self.download_task.connect("finish", self.download_finish)
            self.download_task.connect("error",  self.download_failed)
            self.download_task.connect("start",  self.download_start)

    def load_game(self):
        self.loading = False
        self.send_message('load_uri', 'file://' + self.swf_save_path)
        record_info.record_recent_play(self.appid, self.conf_db)
            
    def run(self):
        self.call_flash_game(self.appid)
        self.start_loading()
        self.application.run()

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

        self.socket_box = gtk.VBox()
        self.socket_box.connect("realize", self._add_socket)

        self.pack_start(self.socket_box, True, True)

    def expose(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation

        cr.set_source_rgba(*alpha_color_hex_to_cairo(('#ff0000', 1.0)))
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        
    def _add_socket(self, w):
        #must create an new socket, because socket will be destroyed when it reparent!!!
        if self.socket:
            self.socket.destroy()
        self.socket = gtk.Socket()
        self.socket_box.pack_start(self.socket, True, True)
        self.socket.realize()

    def add_plug_id(self, plug_id):
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
        #bus_name = dbus.service.BusName(GAME_PLAYER_DBUS_NAME, session_bus)
            
        try:
            Player(session_bus, sys.argv[1:], GAME_PLAYER_DBUS_NAME, GAME_PLAYER_DBUS_PATH).run()
        except KeyboardInterrupt:
            pass
