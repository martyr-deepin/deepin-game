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

import logging

class Logger(logging.Logger):

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def __init__(self, name, level):
        logging.Logger.__init__(self, name, level)
        self.name = name
        self.level = level

    def set_file_log(self, log_path, level=None):
        self.file_handler = logging.FileHandler(log_path)
        self.file_handler.setFormatter(self.formatter)
        if not level:
            self.file_handler.setLevel(self.level)
        else:
            self.file_handler.setLevel(level)

        self.addHandler(self.file_handler)

    def set_console_log(self, level):
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.formatter)
        if not level:
            self.console_handler.setLevel(self.level)
        else:
            self.console_handler.setLevel(level)

        self.addHandler(self.console_handler)

logger = Logger('deepin-game-center', logging.NOTSET)
logger.set_console_log(logging.DEBUG)
logger.set_file_log('/tmp/deepin-game-center.log', logging.INFO)
