#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

try:
    import deepin_pulseaudio_small as deepin_pulseaudio
except ImportError:
    print "----------Please Install Deepin Pulseaudio Python Binding----------"   
    print "git clone git@github.com:linuxdeepin/pypulseaudio.git"
    print "------------------------------------------------------------------"   
    exit(1)

# server_cb(dp_pa, dict)
#   dict: server info

# card_cb(dp_pa, dict, int)
#   dict: card info
#   int: card index

# sink_cb(dp_pa, dict, tuple/None, list, dict, int)
#   dict: sink channel info
#   tuple: sink active port. (name, description, available). or None
#   list: sink volume
#   dict: sink info
#   int: sink index

# source_cb(dp_pa, dict, tuple/None, list, dict, int)
#   dict: source channel info
#   tuple: source active port. (name, description, available). or None
#   list: source volume
#   dict: source info
#   int: source index

# sinkinput_state_cb(dp_pa, dict, int)
#   dict: sinkinput info
#   int: sinkinput index

# sourceoutput_state_cb(dp_pa, dict, int)
#   dict: sourceoutput info
#   int: sourceoutput index

# record_stream_read_cb(obj, value):
#   value: stream fragment data of buffer

# record_stream_suspended(obj):


MAX_VOLUME_VALUE = deepin_pulseaudio.VOLUME_UI_MAX
NORMAL_VOLUME_VALUE = deepin_pulseaudio.VOLUME_NORM

server_info = {}
card_devices = {}

output_devices = {}
output_channels = {}
output_active_ports = {}
output_volumes = {}

input_devices = {}
input_channels = {}
input_active_ports = {}
input_volumes = {}

playback_info = {}
record_info = {}

PULSE = deepin_pulseaudio.new()

def get_volume_balance(channel_num, volume_list, channel_list):
    return deepin_pulseaudio.volume_get_balance(channel_num, volume_list, channel_list)

def get_fallback_sink_name():
    if 'fallback_sink' in server_info:
        return server_info['fallback_sink']
    else:
        return None
    
def get_fallback_sink_index():
    if 'fallback_sink' in server_info:
        name = server_info['fallback_sink']
    else:
        return None
    try:
        for key in output_devices.keys():
            if name == output_devices[key]['name']:
                return key
    except:
        pass
    return None

def get_fallback_source_name():
    if 'fallback_source' in server_info:
        return server_info['fallback_source']
    else:
        return None
    
def get_fallback_source_index():
    if 'fallback_source' in server_info:
        name = server_info['fallback_source']
    else:
        return None
    try:
        for key in input_devices.keys():
            if name == input_devices[key]['name']:
                return key
    except:
        pass
    return None
