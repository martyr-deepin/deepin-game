from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import Request

from myproject.items import AppItem

class Game360Spider(BaseSpider):
    name = 'game360'
    allowed_domains = ['cdn.apc.360.cn']
    start_urls = ['http://cdn.apc.360.cn/index.php?c=GameBox&a=indexV3&cid=5']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        apps = hxs.select('//div/ul[@class="game-sift"]/li') 
        for app in apps:
            appid = app.select('@id').extract()[0].encode("utf-8")
            if appid.startswith("data-"):
                app_item = AppItem()
                app_item['appid'] = appid[5:]
                app_item['name'] = app.select('a/text()').extract()[0].encode('utf-8')
                _tags = []
                for tag in app.select('p/a/text()'):
                    _tags.append(tag.extract().encode('utf-8'))
                app_item['tags'] = ", ".join(_tags)
                yield app_item

        for url in hxs.select('//a/@href').extract():
            #self.log("URL: %s" % url)
            if url.startswith("/index.php?"):
                url = "http://" + response.url.split("/")[2] + url
            try:
                yield Request(url, callback=self.parse)
            except:
                pass
