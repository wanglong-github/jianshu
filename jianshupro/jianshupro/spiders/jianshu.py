import scrapy


class JianshuSpider(scrapy.Spider):
    name = 'jianshu'
    allowed_domains = ['www.jianshu.com']
    start_urls = ['http://www.jianshu.com/']

    def parse(self, response):
        pass
