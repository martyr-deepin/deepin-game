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
import gobject
import pypulse_small as pypulse

class SoundSetting(gobject.GObject):
    '''sound setting class'''

    __gsignals__ = {
        "mute-state" : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
    }

    def __init__(self, current_sink_callback=None):
        super(SoundSetting, self).__init__()

        self.image_widgets = {}
        self.label_widgets = {}
        self.button_widgets = {}
        self.adjust_widgets = {}
        self.scale_widgets = {}
        self.alignment_widgets = {}
        self.container_widgets = {}
        self.view_widgets = {}

        self.__fallback_sink_index = None
        self.__fallback_source_index = None
        self.__state_cb_fun = {}
        self.__state_cb_fun["server"] = self.__server_state_cb
        self.__state_cb_fun["sink"] = self.__sink_state_cb
        self.__state_cb_fun["source"] = self.__source_state_cb
        self.__state_cb_fun["sinkinput"] = self.__sinkinput_state_cb
        #self.__state_cb_fun["card"] = self.__card_state_cb

        self.__record_stream_cb_fun = {"read": self.__record_stream_read_cb, "suspended": self.__record_stream_suspended}

        # pulseaudio signals
        pypulse.PULSE.connect_to_pulse(self.__state_cb_fun)
        pypulse.PULSE.connect("sink-removed", self.pa_sink_removed_cb)
        pypulse.PULSE.connect("source-removed", self.pa_source_removed_cb)
        pypulse.PULSE.connect("card-removed", self.pa_card_removed_cb)
        #pypulse.PULSE.connect("server-changed", self.pa_server_changed_cb)
        self.current_sink_callback = current_sink_callback

    # pulseaudio signals
    def __server_state_cb(self, obj, dt):
        pypulse.server_info = dt
        fallback_sink = pypulse.get_fallback_sink_index()
        if self.__fallback_sink_index != fallback_sink:
            self.__fallback_sink_index = fallback_sink
            if self.__fallback_sink_index in pypulse.output_volumes:
                #self.__set_output_status()
                #self.__set_output_port_status()
                #self.__set_output_treeview_status()
                pass

        fallback_source = pypulse.get_fallback_source_index()
        if self.__fallback_source_index is None and fallback_source is None:
            obj.connect_record(self.__record_stream_cb_fun)
        if self.__fallback_source_index != fallback_source:
            self.__fallback_source_index = fallback_source
            obj.connect_record(self.__record_stream_cb_fun)
            if self.__fallback_source_index in pypulse.input_volumes:
                #self.__set_input_status()
                #self.__set_input_port_status()
                #self.__set_input_treeview_status()
                pass

    def __record_stream_read_cb(self, obj, value):
        #print "stream record:", value
        #self.scale_widgets["input_test"].set_progress(int(round(value, 2) * 100))
        pass

    def __record_stream_suspended(self, obj):
        print "suspended"
        #self.scale_widgets["input_test"].set_progress(0)

    def __sink_state_cb(self, obj, channel, port, volume, sink, idx):
        if idx in pypulse.output_devices:
            op = "changed"
        else:
            op = "new"
        pypulse.output_channels[idx] = channel
        pypulse.output_active_ports[idx] = port
        pypulse.output_volumes[idx] = volume
        pypulse.output_devices[idx] = sink
        if self.__fallback_sink_index is None and pypulse.get_fallback_sink_name() == sink['name']:
            self.__fallback_sink_index = idx
        if self.__fallback_sink_index == idx:
            #self.__set_output_status()
            #self.__set_output_port_status()
            state = pypulse.output_devices[self.__fallback_sink_index]['mute']
            self.emit("mute-state", state)
        if op == "new":
            #self.__set_output_treeview_status()
            pass

    def set_current_sink_callback(self, callback):
        self.current_sink_callback = callback

    def __sinkinput_state_cb(self, obj, dt, index):
        if self.current_sink_callback:
            self.current_sink_callback(dt, index)

    def __source_state_cb(self, obj, channel, port, volume, source, idx):
        if idx in pypulse.input_devices:
            op = "changed"
        else:
            op = "new"
        pypulse.input_channels[idx] = channel
        pypulse.input_active_ports[idx] = port
        pypulse.input_volumes[idx] = volume
        pypulse.input_devices[idx] = source
        if self.__fallback_source_index is None and pypulse.get_fallback_source_name() == source['name']:
            self.__fallback_source_index = idx
        if self.__fallback_source_index == idx:
            #self.__set_input_status()
            #self.__set_input_port_status()
            pass
        if op == "new":
            #self.__set_input_treeview_status()
            pass

    def __card_state_cb(self, obj, dt, idx):
        if idx in pypulse.card_devices:
            op = "changed"
        else:
            op = "new"
        pypulse.card_devices[idx] = dt
        if op == "new":
            #self.__set_card_treeview_status()
            pass

    # pulseaudio remove signal
    def pa_sink_removed_cb(self, obj, index):
        if index in pypulse.output_devices:
            del pypulse.output_devices[index]
        if index in pypulse.output_channels:
            del pypulse.output_channels[index]
        if index in pypulse.output_active_ports:
            del pypulse.output_active_ports[index]
        if index in pypulse.output_volumes:
            del pypulse.output_volumes[index]
        #self.__set_output_treeview_status()

    def pa_source_removed_cb(self, obj, index):
        if index in pypulse.input_devices:
            del pypulse.input_devices[index]
        if index in pypulse.input_channels:
            del pypulse.input_channels[index]
        if index in pypulse.input_active_ports:
            del pypulse.input_active_ports[index]
        if index in pypulse.input_volumes:
            del pypulse.input_volumes[index]
        #self.__set_input_treeview_status()

    def pa_card_removed_cb(self, obj, index):
        if index in pypulse.card_devices:
            del pypulse.card_devices[index]
        #self.__set_card_treeview_status()

