#!/usr/bin/env python

import os
import sys
from deepin_utils.file import get_parent_dir, touch_file_dir

desc_dir = os.path.join(get_parent_dir(__file__), 'app_theme')
old_dir = os.path.join(get_parent_dir(__file__, 2), 'deepin-media-player-private/app_theme')

if __name__ == '__main__':
    name = sys.argv[1]
    for color in os.listdir(desc_dir):
        old_path = os.path.join(old_dir, color, "image", name)
        desc_path = os.path.join(desc_dir, color, 'image', name)
        touch_file_dir(desc_path)
        os.system("cp %s %s" % (old_path, desc_path))
        print "copy: %s -> %s" % (old_path, desc_path)
