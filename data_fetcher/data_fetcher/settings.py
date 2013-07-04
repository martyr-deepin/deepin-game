# Scrapy settings for data_fetcher project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
import os

def setup_django_env(path):
    import imp, os
    from django.core.management import setup_environ
    f, filename, desc = imp.find_module('settings', [path])
    project = imp.load_module('settings', f, filename, desc)

    setup_environ(project)

    import sys
    sys.path.append(os.path.abspath(os.path.join(path, os.path.pardir)))

game_center_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
setup_django_env(os.path.join(game_center_root_dir, "data_manager", "deepin_game_center"))

BOT_NAME = 'data_fetcher'

SPIDER_MODULES = ['data_fetcher.spiders']
NEWSPIDER_MODULE = 'data_fetcher.spiders'

USER_AGENT = 'User-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.4 ' \
                   '(KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4'

ITEM_PIPELINES = [
        'data_fetcher.pipelines.DuplicatesPipeline'
        ]
LOG_LEVEL = "INFO"
