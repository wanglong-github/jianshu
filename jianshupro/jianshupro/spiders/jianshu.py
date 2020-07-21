import scrapy
from scrapy import Request
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
    start_page=2

    #start_requests方法是spider爬虫的启动方法，作用读取start_urls起始网址列表
    #向爬虫引擎发送Request对象，让引擎回调parse方法
    def start_requests(self):
        print('执行start_requests...')
        yield Request(url='https://www.jianshu.com/recommendations/users?page=1',
                      headers=self.ajax_headers)

    def parse(self, response):
        #解析当前作者个人页面url
        auth_list=response.xpath('//div[@class="wrap"]/a/@href').extract()
        # print(f'作者地址：{auth_list}')
        for au in auth_list:
            #获取作者id
            slug_id=au.split('/')[-1]
            #按照作者slug_id获取对应请求作者首页的地址
            au_url=f'https://www.jianshu.com/u/{slug_id}'
            #压入解析作者首页信息请求对象
            yield Request(url=au_url,callback=self.parse_auth,
                          headers=self.ajax_headers,meta={'slug':slug_id})



        #生成新网址
        nurl=f'https://www.jianshu.com/recommendations/users?page={self.start_page}'
        self.start_page+=1
        if self.start_page<101:
            yield Request(url=nurl,callback=self.parse,
                          headers=self.ajax_headers)

    def parse_auth(self,response):
        #解析作者首页信息
        #获取Request.meta.slug
        slug=response.meta['slug']
        print(f'作者标识:{slug}')
