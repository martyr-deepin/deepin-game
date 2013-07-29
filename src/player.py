#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from dtk.ui.init_skin import init_theme
init_theme()
from dtk.ui.application import Application
from dtk.ui.browser import WebView
from deepin_utils.file import get_parent_dir

data_dir = os.path.join(get_parent_dir(__file__, 2), "data")

class Player(object):
    def __init__(self, path, title, width, height):
        self.application = Application()
        self.application.add_titlebar(app_name=title)
        self.application.set_default_size(width, height + self.application.titlebar.size_request()[1])

        webview = WebView()
        webview.open("file://" + path)
        self.application.main_box.pack_start(webview)

    def run(self):
        self.application.run()

def test():
    path = os.path.join(data_dir, "game.swf")
    title = "黄金矿工"
    width = 600
    height = 450
    Player(path, title, width, height).run()

if __name__ == '__main__':
    test()
