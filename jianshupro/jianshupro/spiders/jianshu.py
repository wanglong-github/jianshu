import scrapy
from scrapy import Request
from fake_useragent import UserAgent

from jianshupro.items import JianshuproItem


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
    #当前作者的粉丝数量
    follow_num={}

    #start_requests方法是spider爬虫的启动方法，作用读取start_urls起始网址列表
    #向爬虫引擎发送Request对象，让引擎回调parse方法
    def start_requests(self):
        # print('执行start_requests...')
        # #设置起始页码
        self.fans_start_page=2
        # #设置粉丝数量
        self.fans_num=0
        yield Request(url='https://www.jianshu.com/recommendations/users?page=1',
                      headers=self.base_headers)

    def parse(self, response):
        #解析当前作者个人页面url
        auth_list=response.xpath('//div[@class="wrap"]/a/@href').extract()
        # print(f'作者地址：{auth_list}')
        for au in auth_list:
            #获取作者id
            slug_id=au.split('/')[-1]
            #当前作者粉丝数量
            self.follow_num[slug_id]=0

            #按照作者slug_id获取对应请求作者首页的地址
            au_url=f'https://www.jianshu.com/u/{slug_id}'
            #压入解析作者首页信息请求对象
            yield Request(url=au_url,callback=self.parse_auth,
                          headers=self.base_headers,meta={'slug':slug_id})
            # 通过作者标识，得到对应粉丝页面
            fan_url = f'https://www.jianshu.com/users/{slug_id}/followers'
            yield Request(url=fan_url, callback=self.parse_fans,
                          headers=self.base_headers, meta={'slug': slug_id})
            #解析用户的操作动态信息
            schedule_url=f'https://www.jianshu.com/users/{slug_id}/timeline'
            yield Request(url=schedule_url, callback=self.parse_schedule,
                          headers=self.base_headers, meta={'slug': slug_id})

        #生成新网址
        nurl=f'https://www.jianshu.com/recommendations/users?page={self.start_page}'
        self.start_page+=1
        if self.start_page<101:
            yield Request(url=nurl,callback=self.parse,
                          headers=self.base_headers)

    def parse_auth(self,response):
        #解析作者首页信息
        #获取Request.meta.slug
        slug=response.meta['slug']
        # print(f'作者标识:{slug}')
        item = JianshuproItem()
        #封装解析用户信息
        # 得到个人个人详情界面的主要详情头
        div_main_top = response.xpath('//div[@class="main-top"]')
        #作者标识
        # 昵称
        nickname = div_main_top.xpath('.//div[@class="title"]/a/text()').extract_first()
        # 头像
        head_pic = div_main_top.xpath('.//a[@class="avatar"]/img/@src').extract_first()
        # 是否认证性别
        gender_tmp = div_main_top.xpath('.//div[@class="title"]/i/@class').extract_first()
        # 判断是否认证男女未认证则为No
        if gender_tmp:
            gender = gender_tmp.split('-')[-1]
        else:
            gender = 'No'
        # 得到关注粉丝文章数
        all_nums_first = div_main_top.xpath(
            './/div[@class="info"]/ul/li/div[@class="meta-block"]/a/p/text()').extract()
        # 关注
        following_num = all_nums_first[0]
        # 粉丝
        followers_num = all_nums_first[1]
        # 文章
        articles_num = all_nums_first[2]
        # 得到字数收获喜欢总资产数
        all_nums_second = div_main_top.xpath(
            './/div[@class="info"]/ul/li/div[@class="meta-block"]/p/text()').extract()
        # 字数
        words_num = all_nums_second[0]
        # 收获喜欢
        be_liked_num = all_nums_second[1]


        item['nickname'] = nickname
        item['slug'] = slug
        item['head_pic'] = head_pic
        item['gender'] = gender
        item['following_num'] = int(following_num)
        item['followers_num'] = int(followers_num)
        #得到粉丝的状态

        self.follow_num[slug]=int(followers_num)

        item['articles_num'] = int(articles_num)
        item['words_num'] = int(words_num)
        item['be_liked_num'] = int(be_liked_num)
        yield item

    def parse_fans(self,response):
        # 解析作者对应粉丝信息
        slug = response.meta['slug']
        # print(f'解析作者对应粉丝信息，作者标识:{slug}')
        # #设置起始页码
        # self.fans_start_page=2
        # #设置粉丝数量
        # self.fans_num=0
        ulist=response.xpath('//div[@id="list-container"]/ul[@class="user-list"]/li')
        for u in ulist:
            #解析每一个粉丝对象，发送到管道中
            item=JianshuproItem()
            #昵称
            nick=u.xpath('./div[@class="info"][1]/a/text()').extract_first()

            #获取关注、粉丝数、文章数
            temp=u.xpath('./div[@class="info"][1]/div[@class="meta"][1]/span/text()').extract()
            arr_temp=[]
            for t in temp:
                arr=t.split(" ")[-1]
                arr_temp.append(arr)
            print(f'粉丝昵称：{nick}')
            following_num=int(arr_temp[0])
            followers_num=int(arr_temp[1])
            articles_num=int(arr_temp[2])
            item['nickname']=nick
            item['following_num']=following_num
            item['followers_num']=followers_num
            item['articles_num']=articles_num

            yield item
            #对粉丝进行计数
            self.fans_num+=1
            #判断粉丝获取是否结束
            if self.fans_num > self.follow_num[slug]:
                break
        #获取粉丝分页url
        xurl=f'https://www.jianshu.com/users/51b4ef597b53/followers?page={self.fans_start_page}'
        self.fans_start_page+=1
        if self.fans_num < self.follow_num[slug]:
            yield Request(url=xurl, callback=self.parse_fans,
                          headers=self.base_headers,meta={'slug':slug})


    def parse_schedule(self,response):
        # 解析当前作者动态信息
        slug = response.meta['slug']
        print(f'解析当前作者动态信息，作者标识:{slug}')