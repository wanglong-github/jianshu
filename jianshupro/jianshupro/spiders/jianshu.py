import scrapy
from requests import Request
from fake_useragent import UserAgent

class JianshuSpider(scrapy.Spider):
    name = 'jianshu'
    # allowed_domains = ['www.jianshu.com']
    # start_urls = ['http://www.jianshu.com/']

    #随机用户代理
    base_headers = {'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
                    'Host': 'www.jianshu.com',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html, */*; q=0.01',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                    'Connection': 'keep-alive',
                    'Referer': 'http://www.jianshu.com'}
    # 只加载列表模块
    ajax_headers = dict(base_headers, **{"X-PJAX": "true", 'User-Agent': UserAgent().random})

    #start_requests方法是spider爬虫的启动方法，作用读取start_urls起始网址列表
    #向爬虫引擎发送Request对象，让引擎回调parse方法
    def start_requests(self):
        print('执行start_requests...')
        yield Request(url='jianshu.com/recommendations/users?page=1',
                      headers=self.ajax_headers)

    def parse(self, response):
        print('执行parse...')
