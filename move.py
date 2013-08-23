#!/usr/bin/env python

import os
import sys
from deepin_utils.file import get_parent_dir, touch_file_dir

desc_dir = os.path.join(get_parent_dir(__file__), 'app_theme')
old_dir = os.path.join(get_parent_dir(__file__, 2), 'deepin-music-player-private/app_theme')

def copy_to_mytheme():
    names = sys.argv[1::]
    for name in names:
        for color in os.listdir(desc_dir):
            old_path = os.path.join(old_dir, color, "image", name)
            desc_path = os.path.join(desc_dir, color, 'image', name)
            touch_file_dir(desc_path)
            os.system("cp %s %s" % (old_path, desc_path))
            print "copy: %s -> %s" % (old_path, desc_path)

def dir_rename(old, new):
    colors = os.listdir(desc_dir)
    for color in colors:
        old_dir = os.path.join(desc_dir, color, 'image', old)
        new_dir = os.path.join(desc_dir, color, 'image', new)
        if os.path.isdir(old_dir):
            os.system('mv %s %s' % (old_dir, new_dir))
            print 'mv %s %s' % (old_dir, new_dir)
        else:
            print "Error old dir:", old_dir

def rename_file(folder, old, new):
    colors = os.listdir(desc_dir)
    for color in colors:
        old_file = os.path.join(desc_dir, color, 'image', folder, old)
        new_file = os.path.join(desc_dir, color, 'image', folder, new)
        if os.path.exists(old_dir):
            os.system('mv %s %s' % (old_file, new_file))
            print 'mv %s %s' % (old_file, new_file)
        else:
            print "Error old dir:", old_file
            
if __name__ == '__main__':
    pass
    #copy_to_mytheme()
    #dir_rename('favotite', 'favorite')
    #files = [
            #('favotite_normal.png', 'favorite_normal.png'),
            #('favotite_hover.png', 'favorite_hover.png'),
            #('favotite_press.png', 'favorite_press.png'),
            #('unfavotite_normal.png', 'unfavorite_normal.png'),
            #('unfavotite_hover.png', 'unfavorite_hover.png'),
            #('unfavotite_press.png', 'unfavorite_press.png'),
            #]
    #for (old, new) in files:
        #rename_file('favorite', old, new)
