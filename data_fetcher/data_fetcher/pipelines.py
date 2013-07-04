# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from game360.models import App

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        appid = item['appid']
        if appid in self.ids_seen or App.objects.filter(appid=appid):
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['appid'])
            #item.save()
            return item
