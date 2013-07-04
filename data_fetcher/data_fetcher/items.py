# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.contrib.djangoitem import DjangoItem
from game360.models import App

from scrapy.item import Item, Field

class AppItem(DjangoItem):
    django_model = App

class MyProjectjectItem(Item):
    appid = Field()
    name = Field()
    tags = Field()
