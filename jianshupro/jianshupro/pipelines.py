# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from itemadapter import ItemAdapter

from jianshupro.items import JianshuproItem


class JianshuproPipeline:
    # 在管道中首先连接数据库
    def open_spider(self, spider):
        self.client = pymongo.MongoClient('127.0.0.1')
        self.db = self.client['jianshu']

    def close_spider(self, spider):
        self.client.close()
    def process_item(self, item, spider):
        if isinstance(item,JianshuproItem):
            #  插入新的用户信息
            self.db['tabuser'].update({'slug': item['slug']}, {'$setOnInsert': item}, upsert=True)
            print(f'获取用户信息:{item}')
        elif isinstance(item,dict):
            self.db['tabtimeline'].update({'slug': item['slug']}, {'$setOnInsert': item}, upsert=True)
            print(f'获取到用户动态信息{item}')
        return item
