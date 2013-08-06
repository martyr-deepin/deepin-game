#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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

from search_page import SearchPage
from nls import _
from constant import APP_DBUS_NAME, APP_OBJECT_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
from deepin_utils.file import get_parent_dir
from dtk.ui.application import Application
from dtk.ui.slider import HSlider
from dtk.ui.theme import ui_theme
from dtk.ui.draw import draw_text, draw_vlinear
from dtk.ui.treeview import TreeItem
from dtk.ui.breadcrumb import Crumb
from dtk.ui.utils import color_hex_to_cairo, propagate_expose
from deepin_utils.ipc import is_dbus_name_exists
from content_page import ContentPageInfo
from action_bar import ActionBar
from navigate_page import NavigatePage
from foot_box import FootBox
from bluetooth_dialog import BluetoothProgressDialog, BluetoothReplyDialog
import gtk
import subprocess
import os
from module_info import get_module_infos
from dbus.mainloop.glib import DBusGMainLoop
import sys
import dbus
import dbus.service
import dbus
import dbus.service
import getopt

MAIN_MODULE = "main"

module_history = [MAIN_MODULE]
module_history_index = 0

preview_module_id = None

def record_module_history(module_name):
    global module_history
    global module_history_index
    
    (backward_modules, forward_modules) = module_history[0:module_history_index], module_history[module_history_index::]
    
    backward_modules = filter(lambda backward_module: backward_module != module_name, backward_modules)
    forward_modules = filter(lambda forward_module: forward_module != module_name, forward_modules)
    module_history_index = len(backward_modules)
    module_history = backward_modules + [module_name] + forward_modules
    
    return len(backward_modules), len(forward_modules)

def get_backward_module():
    global module_history
    global module_history_index
    
    if module_history_index == 0:
        return None
    else:
        module_history_index = max(0, module_history_index - 1)
        
        return module_history[module_history_index]

def get_forward_module():
    global module_history
    global module_history_index

    if module_history_index == len(module_history) - 1:
        return None
    else:
        module_history_index = min(len(module_history) - 1, module_history_index + 1)
        
        return module_history[module_history_index]

def call_module_by_name(module_name, module_dict, slider, content_page_info, force_direction=None, module_uid=None):
    if module_dict.has_key(module_name):
        start_module_process(slider,                                         
                             content_page_info,                              
                             module_dict[module_name].path,                  
                             module_dict[module_name].config,
                             force_direction, 
                             module_uid)

class ThemeItem(TreeItem):
    ITEM_HEIGHT = 20
    ITEM_WIDTH = 100
    
    def __init__(self, name):
        TreeItem.__init__(self)
        self.name = name

    def __render_name(self, cr, rect):                                          
        font_color = ui_theme.get_color("menu_font").get_color()
        '''
        cr.set_source_rgb(1, 1, 1)                                              
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)                   
        cr.fill()
        '''
        if self.is_hover:                                                       
            # Draw background.                                                  
            draw_vlinear(cr, rect.x, rect.y, rect.width, rect.height,           
                         ui_theme.get_shadow_color("menu_item_select").get_color_info())
            font_color = ui_theme.get_color("menu_select_font").get_color()
                                                                                
        draw_text(cr,                                                           
                  self.name,                                       
                  rect.x + 10,                                                   
                  rect.y,                                                       
                  self.ITEM_WIDTH,                                               
                  rect.height, 
                  text_color=font_color)

    def button_press(self, column, offset_x, offset_y):
        send_message("individuation", "switch-theme", self.name)

    def get_height(self):
        return self.ITEM_HEIGHT

    def get_width(self):                                                
        return self.ITEM_WIDTH                                  
    
    def get_column_widths(self):
        return [self.ITEM_WIDTH]

    def get_column_renders(self):                                               
        return [self.__render_name]                                             

    def unhover(self, column, offset_x, offset_y):                              
        self.is_hover = False                                                   
                                                                                
        if self.redraw_request_callback:                                        
            self.redraw_request_callback(self)                                  
                                                                                
    def hover(self, column, offset_x, offset_y):                                
        self.is_hover = True                                                    
                                                                                
        if self.redraw_request_callback:                                        
            self.redraw_request_callback(self)

class DBusService(dbus.service.Object):
    def __init__(self, 
                 action_bar, 
                 content_page_info, 
                 application=None,
                 module_dict=None,
                 slider=None, 
                 foot_box=None
                 ):
        # Init dbus object.
        bus_name = dbus.service.BusName(APP_DBUS_NAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, APP_OBJECT_NAME)
        self.bluetooth_progress_dialog = None

        # Define DBus method.
        def unique(self, module_name):
            global preview_module_id
            
            if application:
                if module_name != "" and preview_module_id != module_name:
                    action_bar.bread.remove_node_after_index(0)
                    call_module_by_name(module_name, module_dict, slider, content_page_info, "right", "")
                
                application.raise_to_top()
        
        def message_receiver(self, *message):
            (message_type, message_content) = message
            if message_type == "send_plug_id":
                (module_id, plug_id) = message_content
                content_page = content_page_info.get_content_page(module_id)
                content_page.add_plug_id(plug_id)
            elif message_type == "send_module_info":
                (crumb_index, (module_id, crumb_name), argv) = message_content
                if argv == "":
                    action_bar.bread.remove_node_after_index(0)
                    action_bar.bread.add(Crumb(crumb_name, None))
                else:
                    menu_items = [ThemeItem(x) for x in argv.split(';') if x.strip()]
                    action_bar.bread.add(Crumb(crumb_name, menu_items))
                
                backward_module_id, forward_module_id = record_module_history(module_id)
                self.__set_ward(backward_module_id, forward_module_id)
            elif message_type == "send_submodule_info":
                (crumb_index, crumb_name, module_id) = message_content
                action_bar.bread.remove_node_after_index(1)
                action_bar.bread.add(Crumb(crumb_name, None)) 
                backward_module_id, forward_module_id = record_module_history(module_id)
                self.__set_ward(backward_module_id, forward_module_id)
            elif message_type == "change_crumb":
                crumb_index = message_content
                action_bar.bread.remove_node_after_index(crumb_index)
            elif message_type == "goto":
                (module_id, module_uid) = message_content
                action_bar.bread.remove_node_after_index(0)
                call_module_by_name(module_id, module_dict, slider, content_page_info, "right", module_uid)
                
                backward_module_id, forward_module_id = record_module_history(module_id)
                self.__set_ward(backward_module_id, forward_module_id)
            elif message_type == "back":
                index = message_content
                action_bar.bread.remove_node_after_index(index)
                
            elif message_type == "status":
                (module_id, status) = message_content
                if foot_box:
                    foot_box.show(module_id)
                    if status == "hide_reset":
                        foot_box.hide_reset()
                    elif status == "show_reset":
                        foot_box.show_reset()
                    else:
                        foot_box.set_status(status)
            elif message_type == "dialog":
                (module_id, dialog_type, message, argv) = message_content
                if module_id == "bluetooth":
                    if dialog_type == "progress":
                        if argv == "":
                            self.bluetooth_progress_dialog = BluetoothProgressDialog(
                                cancel_cb = self.__on_bluetooth_cancel)
                            self.bluetooth_progress_dialog.set_message(message)
                            self.bluetooth_progress_dialog.show_all()
                        elif argv == "-1":
                            self.bluetooth_progress_dialog.destroy()
                        else:
                            self.bluetooth_progress_dialog.set_progress(int(argv))
                    elif dialog_type == "reply":
                        is_succeed = True
                        if argv == "False":
                            is_succeed = False
                        reply_dlg = BluetoothReplyDialog(message, is_succeed = is_succeed)
                        print "*************: %s" % application.window
                        reply_dlg.show_all()
                        reply_dlg.place_center(application.window) 
            else:
                print message
                    
        # Below code export dbus method dyanmically.
        # Don't use @dbus.service.method !
        setattr(DBusService, 
                'message_receiver', 
                dbus.service.method(APP_DBUS_NAME)(message_receiver))
        setattr(DBusService, 
                'unique', 
                dbus.service.method(APP_DBUS_NAME)(unique))

    def __set_ward(self, backward_module_count=None, forward_module_count=None):
        if backward_module_count:
            action_bar.forward_button.set_sensitive(True)
            action_bar.forward_button.set_active(True)
        else:
            action_bar.forward_button.set_sensitive(False)
            action_bar.forward_button.set_active(False)

        if forward_module_count:
            action_bar.backward_button.set_sensitive(True)
            action_bar.backward_button.set_active(True)
        else:
            action_bar.backward_button.set_sensitive(False)
            action_bar.backward_button.set_active(False)
    
    def __on_bluetooth_cancel(self):
        send_message("bluetooth", "cancel", "progress cancel")

def handle_dbus_reply(*reply):
    #print "com.deepin.system_settings (reply): %s" % (str(reply))
    pass
    
def handle_dbus_error(*error):
    print "com.deepin.system_settings (error): %s" % (str(error))

def titlebar_forward_cb(module_dict, action_bar, slider, content_page_info, foot_box):
    module_id = get_backward_module()
    if module_id:
        action_bar.bread.remove_node_after_index(0)
        if module_id == MAIN_MODULE:
            slider.slide_to_page(navigate_page, "none")

            foot_box.hide()
        else:
            call_module_by_name(module_id, module_dict, slider, content_page_info, "right")

def titlebar_backward_cb(module_dict, action_bar, slider, content_page_info, foot_box):
    module_id = get_forward_module()
    if module_id:
        action_bar.bread.remove_node_after_index(0)
        if module_id == MAIN_MODULE:
            slider.slide_to_page(navigate_page, "left")

            foot_box.hide()
        else:
            call_module_by_name(module_id, module_dict, slider, content_page_info, "left")

def search_cb(action_bar, slider, foot_box):
    keyword = action_bar.search_entry.get_text()
    if keyword.strip() != "":
        search_page.query(keyword)
        action_bar.bread.remove_node_after_index(0)
        slider.slide_to_page(search_page, "left")

    foot_box.hide()

def send_message(module_id, message_type, message_content):
    bus = dbus.SessionBus()
    module_dbus_name = "com.deepin.%s_settings" % (module_id)
    module_object_name = "/com/deepin/%s_settings" % (module_id)
    if is_dbus_name_exists(module_dbus_name):
        bus_object = bus.get_object(module_dbus_name, module_object_name)
        method = bus_object.get_dbus_method("message_receiver")
        method(message_type, 
               message_content,
               reply_handler=handle_dbus_reply,
               error_handler=handle_dbus_error
               )
        
def switch_page(bread, content_page_info, index, label, slider, navigate_page, foot_box):
    global preview_module_id

    if index == 0:
        if label == _("System Settings"):
            slider.slide_to_page(navigate_page, "left")
            content_page_info.set_active_module_id("main")
            foot_box.hide()
            if preview_module_id:                                                       
                send_message(preview_module_id, "exit", "")
    else:
        send_message(content_page_info.get_active_module_id(),
                     "click_crumb",
                     (index, label))
        
def click_module_menu_item(slider, content_page_info, action_bar, module_info, foot_box):
    if module_info.id != content_page_info.get_active_module_id():
        foot_box.hide()
        action_bar.bread.remove_node_after_index(0)
        start_module_process(slider, content_page_info, module_info.path, module_info.config)
        
def add_crumb(index, label):
    print (index, label)

def start_module_process(slider, content_page_info, module_path, module_config, force_direction=None, 
                         module_uid=None):
    global preview_module_id

    module_id = module_config.get("main", "id")
    module_slide_to_page = True
    if module_config.has_option("main", "slide_to_page"):
        if module_config.get("main", "slide_to_page") == "False":
            module_slide_to_page = False

    content_page = content_page_info.get_content_page(module_id)
    content_page_info.set_active_module_id(module_id)
    
    if module_slide_to_page:
        if force_direction:
            slider.slide_to_page(content_page, force_direction)
        else:
            slider.slide_to_page(content_page, "right")
    
    module_dbus_name = "com.deepin.%s_settings" % (module_id)
    if not is_dbus_name_exists(module_dbus_name):
        if module_uid:
            subprocess.Popen("python %s %s" % (os.path.join(module_path, module_config.get("main", "program")), module_uid), shell=True)            
        else:
            subprocess.Popen("python %s" % (os.path.join(module_path, module_config.get("main", "program"))), shell=True)
    else:
        if module_uid:
            send_message(module_id, "show_again", module_uid)
        else:
            send_message(module_id, "show_again", "")

    preview_module_id = module_id

def is_exists(app_dbus_name, app_object_name, module_name):                                  
    """                                                                         
    Check the program or service is already started by its app_dbus_name and app_object_name.
                                                                                
    @param app_dbus_name: the public service name of the service.               
    @param app_object_name: the public service path of the service.             
    @return: If the service is already on, True is returned. Otherwise return False.
    """                                                                         
    DBusGMainLoop(set_as_default=True) # WARING: only use once in one process   
                                                                                
    # Init dbus.                                                                
    bus = dbus.SessionBus()                                                     
    if bus.request_name(app_dbus_name) != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
        method = bus.get_object(app_dbus_name, app_object_name).get_dbus_method("unique")
        method(module_name) 
                                                                                
        return True                                                             
    else:                                                                       
        return False       

def application_focus_changed_cb(widget, event, tp):
    if preview_module_id:
        send_message(preview_module_id, "focus_changed", tp)

if __name__ == "__main__":
    ops, args = getopt.getopt(sys.argv[1:], '')
    module_name = ""

    if len(args):
        module_name = args[0]

    # Check unique.                                                              
    if is_exists(APP_DBUS_NAME, APP_OBJECT_NAME, module_name):                                
        sys.exit()

    # WARING: only use once in one process
    DBusGMainLoop(set_as_default=True) 
    
    # Init application.
    application = Application(resizable=False)
    application.window.connect("focus-out-event", application_focus_changed_cb, "o")
    application.window.connect("focus-in-event", application_focus_changed_cb, "i")

    # Set application default size.
    application.window.set_geometry_hints(
        None,
        WINDOW_WIDTH, WINDOW_HEIGHT,
        WINDOW_WIDTH, WINDOW_HEIGHT,
        )
    image_dir = os.path.join(get_parent_dir(__file__, 2), "image")

    # Set application icon.
    application.set_icon(os.path.join(image_dir, "icon.png"))
    
    # Set application preview pixbuf.
    application.set_skin_preview(os.path.join(image_dir, "frame.png"))
    
    # Add titlebar.
    application.add_titlebar(
        ["min", "close"], 
        os.path.join(image_dir, "logo.png"),
        _("System Settings"),
        enable_gaussian=False,
        name_size=10,
	)
    
    frame_padding = 6
    frame_padding_top = 4

    # Init main box.
    def expose_frame(widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        cr.set_source_rgb(*color_hex_to_cairo("#aeaeae"))
        cr.rectangle(rect.x + frame_padding - 1, rect.y + frame_padding_top, 1, rect.height - frame_padding - frame_padding_top)
        cr.rectangle(rect.x + rect.width - frame_padding, rect.y + frame_padding_top, 1, rect.height - frame_padding - frame_padding_top)
        cr.rectangle(rect.x + frame_padding - 1, rect.y + rect.height - frame_padding, rect.width - frame_padding * 2 + 2, 1)
        cr.fill()
        
        # Propagate expose.
        propagate_expose(widget, event)
        
        return True
    
    main_align = gtk.Alignment()
    main_align.set(0.5, 0.5, 1, 1)
    main_align.set_padding(frame_padding_top, frame_padding, frame_padding, frame_padding)
    main_align.connect("expose-event", expose_frame)
    main_box = gtk.VBox()
    body_box = gtk.VBox()
    foot_box = FootBox()
    
    # Init module infos.
    module_infos = get_module_infos()
    module_dict = {}
    for module_info_list in module_infos:
        for module_info in module_info_list:
            module_dict[module_info.id] = module_info
    
    # Init action bar.
    action_bar = ActionBar(module_infos, 
                           lambda bread, index, label: switch_page(bread, content_page_info, index, label, slider, navigate_page, foot_box),
                           lambda module_info: click_module_menu_item(slider, content_page_info, action_bar, module_info, foot_box), 
                           lambda : titlebar_backward_cb(module_dict, action_bar, slider, content_page_info, foot_box), 
                           lambda : titlebar_forward_cb(module_dict, action_bar, slider, content_page_info, foot_box), 
                           lambda : search_cb(action_bar, slider, foot_box))
    action_bar.backward_button.set_sensitive(False)
    action_bar.forward_button.set_sensitive(False)
    
    # Init slider.
    slider = HSlider(200)

    # Init search page.
    search_page = SearchPage(module_infos)
    
    # Init navigate page.
    navigate_page = NavigatePage(module_infos, lambda path, config: start_module_process(slider, content_page_info, path, config))
    
    # Append widgets to slider.
    slider.append_page(search_page)
    if module_name == "":
        slider.append_page(navigate_page)
        application.window.connect("realize", lambda w: slider.set_to_page(navigate_page))

    foot_box.hide()
    
    # Init content page info.
    content_page_info = ContentPageInfo(slider)
    
    for module_info_list in module_infos:
        for module_info in module_info_list:
            content_page_info.create_content_page(module_info.id)
    
    # Connect widgets.
    body_box.pack_start(slider, True, True)
    main_box.pack_start(action_bar, False, False)
    main_box.pack_start(body_box, True, True)
    main_box.pack_start(foot_box, False, False)
    main_align.add(main_box)
    application.main_box.pack_start(main_align)
    
    # Start dbus service.
    DBusService(action_bar, content_page_info, application, module_dict, slider, foot_box)

    if module_name != "":
        if is_dbus_name_exists(APP_DBUS_NAME):
            bus_object = dbus.SessionBus().get_object(APP_DBUS_NAME, APP_OBJECT_NAME)
            method = bus_object.get_dbus_method("message_receiver") 
            method("goto", 
                    (module_name, ""), 
                    reply_handler=handle_dbus_reply, 
                    error_handler=handle_dbus_error
                  )
    
    application.run()
