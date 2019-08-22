# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .items import *
import  datetime
import  pymongo


class WeiboPipeline(object):
    def parse_data(self, data):
        return data
    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            if item.get('created_at'):
                item['created_at'] = item.get('created_at').strip()
                item['created_at'] = self.parse_data(item['created_at'])

        return item


#添加爬取时间信息
class TimePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, User_Item) or isinstance(item,WeiboItem):
            now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            item['crawler_at'] = now
            print('-'*30)
            print(dict(item))
        return  item


#存储item至mongodb
class  MongoPileline(object):
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    #从settings中获取mongo_url,mongo_db信息，并返回实例
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url= crawler.settings.get('MONGO_URL'),
            mongo_db= crawler.settings.get('MONGO_DB')
        )
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]
        #生成以ID为标准升序排列
        self.db[User_Item.collection].create_index([('id', pymongo.ASCENDING)])
        self.db[WeiboItem.collection].create_index([('id', pymongo.ASCENDING)])

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, User_Item) or isinstance(item, WeiboItem):
            self.db[item.collection].update_one({'id':item.get('id')}, {'$set':item}, True)

        #以用户ID为检索条件，更新关注和粉丝
        if isinstance(item, UserRalationItem):
            self.db[item.collection].update_one(
                {'id':item.get('id')},
                {'$addToSet':
                    {
                        'follows':{'$each':item['follows']},
                        'fans':{'$each':item['fans']}
                    }
                },True)
        return  item
