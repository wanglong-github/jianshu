# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JianshuproItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 昵称
    nickname = scrapy.Field()
    # 标识
    slug = scrapy.Field()
    # 头像
    head_pic = scrapy.Field()
    # 性别
    gender = scrapy.Field()
    # 是否简书认证作者
    is_contract = scrapy.Field()
    # 关注
    following_num = scrapy.Field()
    # 粉丝
    followers_num = scrapy.Field()
    # 文章数
    articles_num = scrapy.Field()
    # 字数
    words_num = scrapy.Field()
    # 收获喜欢
    be_liked_num = scrapy.Field()
