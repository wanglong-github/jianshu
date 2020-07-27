import datetime

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
    timeline_data={}
    # 获取用户动态信息：
    # [{用户id:
    # {'发表评论':[{时间:{其他用户id:评论文字,对应自己文章:文章id}},...]},
    # {'发表文章':[{发表时间:文章id},...]},
    # {'喜欢文章':[{时间：{喜欢文章id},...]},
    # {'赞赏文章':[{时间：{赞赏文章id},...]},
    # {'关注用户':[{时间：{关注用户id},...]},
    # {'关注文集':[{时间：{关注文集id},...]},
    # {'关注专题':[{时间：{关注专题id},...]},
    # {'点赞评论':[{时间：{点赞评论id},...]},
    #
    # },



    #start_requests方法是spider爬虫的启动方法，作用读取start_urls起始网址列表
    #向爬虫引擎发送Request对象，让引擎回调parse方法
    def start_requests(self):
        # print('执行start_requests...')
        # #设置起始页码
        self.fans_start_page=2
        # #设置粉丝数量
        self.fans_num=0
        #起始动态页码
        self.timeline_startpage=2

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

            # 创建当前用户动态信息统计对象
            self.itemdata={}
            self.itemdata['slug']=slug_id
            self.timeline_data['dydata'] = [
                {'comment_note': []},  # 发表评论
                {'like_note': []},  # 喜欢文章
                {'reward_note': []},  # 赞赏文章
                {'share_note': []},  # 发表文章
                {'like_user': []},  # 关注用户
                {'like_collection': []},  # 关注专题
                {'like_comment': []},  # 点赞评论
                {'like_notebook': []},  # 关注文案
            ]

            #按照作者slug_id获取对应请求作者首页的地址
            au_url=f'https://www.jianshu.com/u/{slug_id}'
            #压入解析作者首页信息请求对象
            yield Request(url=au_url,callback=self.parse_auth,
                          headers=self.base_headers,meta={'slug':slug_id})
            # 通过作者标识，得到对应粉丝页面
            fan_url = f'https://www.jianshu.com/users/{slug_id}/followers'
            # yield Request(url=fan_url, callback=self.parse_fans,
            #               headers=self.base_headers, meta={'slug': slug_id})
            #解析用户的操作动态信息
            schedule_url=f'https://www.jianshu.com/users/{slug_id}/timeline'
            yield Request(url=schedule_url, callback=self.parse_schedule,
                          headers=self.base_headers, meta={'slug': slug_id,'xitem':"first"})

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
        # 判断是否认证男女未认证则为No
        if gender_tmp:
            gender = gender_tmp.split('-')[-1]
        else:
            gender = 'No'
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
            # print(f'粉丝昵称：{nick}')
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
        #处理用户动态
        slug = response.meta['slug']
        xitem = response.meta['xitem']
        print(f'第一次:{xitem}')

        if xitem and (xitem == 'first'):
            # 只是在第一个得到用户请求创建一个对象
            self.itemdata = {}
            self.itemdata['slug'] = slug
            self.itemdata['dydata'] = [
                {'comment_note': []},  # '发表评论'
                {'like_note': []},  # '喜欢文章'
                {'reward_note': []},  # '赞赏文章'
                {'share_note': []},  # '发表文章'
                {'like_user': []},  # '关注用户'
                {'like_collection': []},  # '关注专题'
                {'like_comment': []},  # '点赞评论'
                {'like_notebook': []},  # '关注文集'
            ]
        print(f'每次封装动态数据:{self.itemdata}')

        # print(f'解析当前作者动态信息，作者标识:{slug}')
        #获取所有的文章项目
        li=response.xpath('//ul[@class="note-list"]/li')
        if not li:
            #当前用户动态信息爬取结束
            # item={self.timeline_data[slug]}
            # print(f'得到当前用户数据：{item}')
            yield self.itemdata
            return
        #遍历所有文章区域
        for it in li:
            # #获取该元素id属性
            # xid=it.xpath('./@id').extract_first()
            # print(f'动态id：{xid}')

            if it.xpath('.//span[@data-type="comment_note"]'):
                # 发表评论
                xtime = self.extract_time(it,"comment_note")
                #评论文字
                comm_txt=it.xpath('.//span[@data-type="comment_note"]/p/text()').extract_first()
                #对应文章url
                arti_slug=it.xpath('./div[@class="content"]/blockquote/a/@href').extract_first()
                self.itemdata['dydata'][0]['comment_note'].append({xtime: {arti_slug:comm_txt}})
                # print(f'发表评论，文章url:{arti_slug},comm_txt:{comm_txt.strip()},时间：{xtime}')

            elif it.xpath('.//span[@data-type="like_note"]'):
                #获取时间
                xtime = self.extract_time(it, "like_note")
                #喜欢文章id
                xhref=it.xpath('./div[@class="content"]/a[1]/@href').extract_first()
                self.itemdata['dydata'][1]['like_note'].append({xtime:xhref})
                # print(f'喜欢文章url:{xhref},时间:{xtime}')

            elif it.xpath('.//span[@data-type="reward_note"]'):
                # 赞赏文章
                xtime = self.extract_time(it, "reward_note")
                href_id = it.xpath('./div[@class="content"]/a[@class="title"]/@href').extract_first()
                self.itemdata['dydata'][2]['reward_note'].append({xtime: href_id})

            elif it.xpath('.//span[@data-type="share_note"]'):
                # 发表文章
                xtime = self.extract_time(it,"share_note")
                xhref = it.xpath('./div[@class="content"]/a[1]/@href').extract_first()
                self.itemdata['dydata'][3]['share_note'].append({xtime: xhref})

            elif it.xpath('.//span[@data-type="like_user"]'):
                # 关注用户
                xtime = self.extract_time(it, "like_user")
                href_id = it.xpath('./div[@class="follow-detail"]/div/a[@class="title"]/@href').extract_first()
                self.itemdata['dydata'][4]['like_user'].append({xtime: href_id})
                # print(f'关注用户：{xhref},时间：{xtime}')

            elif it.xpath('.//span[@data-type="like_collection"]'):
                # 关注专题
                xtime = self.extract_time(it, "like_collection")
                href_id = it.xpath('./div[@class="content"]/div[@class="follow-detail"]/div/a[class="title"]/@href').extract_first()
                self.itemdata['dydata'][5]['like_collection'].append({xtime: href_id})
                # print(f'关注专题：{href_id},时间：{xtime}')

            elif it.xpath('.//span[@data-type="like_comment"]'):
                # 点赞评论
                xtime = self.extract_time(it, "like_comment")
                # 评论文字
                ctxt = it.xpath('./div[@class="content"]/p/text()').extract_first()
                self.itemdata['dydata'][6]['like_comment'].append({xtime: ctxt.strip()})
            elif it.xpath('.//span[@data-type="like_notebook"]'):
                # 关注文案
                xtime = self.extract_time(it, "like_notebook")
                #文集链接
                href_id = it.xpath(
                    './div[@class="content"]/div[@class="follow-detail"]/div/a[@class="title"]/@href').extract_first()
                self.itemdata['dydata'][7]['like_notebook'].append({xtime: href_id})
        #获取下一页max_id取值
        tid=li[-1].xpath('./@id').extract_first()
        tid=int(tid.split('-')[-1])

        xurl=f'https://www.jianshu.com/users/{slug}/timeline?max_id ={tid-1}&page={self.timeline_startpage}'
        self.timeline_startpage+=1
        #提交下一个分页请求
        yield Request(url=xurl, callback=self.parse_schedule,
                          headers=self.base_headers, meta={'slug': slug,'xitem':'sc'})

    # 获取时间
    def extract_time(self,it,itname):
        xtime = it.xpath(f'.//span[@data-type="{itname}"]/@data-datetime').extract_first()
        xtime = xtime.split('+')[0].replace('T', ' ')
        # xtime = datetime.datetime.strptime(xtime, "%Y-%m-%d %H:%M:%S")
        return xtime
