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

import json

js_str = '''
function append_data_to_gallery(data){
    for (var i=0; i<data.length; i++){
        var grid_div = '';
        grid_div += '<div class="item '+ data[i]['index_pic_wh'] +' caption">';
        grid_div += '<img src="' + data[i]['index_pic_url'] +'">';
        grid_div += '<div class="popup">';
        grid_div += '<h2><big>9</big>.<small>5</small></h2>';
        grid_div += '<h3>' + data[i]['name'] + '</h3>';
        grid_div += '<h4>游戏简介：' + data[i]['summary'] + '</h4>';
        grid_div += '<span class="arrow"></span>';
        grid_div += '</div>';
        grid_div += '<a href="play://'+data[i]['id']+',';
        grid_div += data[i]['name'] +',';
        grid_div += data[i]['width'] + ',';
        grid_div += data[i]['height'] + ',';
        grid_div += data[i]['swf_game'];
        grid_div += '" target="_blank" class="over"></a>';
        grid_div += '<a href="#info" class="info"></a>';
        grid_div += '<span class="icon"></span>';
        grid_div += '</div>';
        $('#grid').append(grid_div);
    }
}
var infos = %s;
append_data_to_gallery(infos);
'''

def generate_content_js(infos):
    contents = js_str % json.dumps(infos)
    with open('/tmp/deepin-game-center/content.js', 'wb') as fp:
        fp.write(contents)

