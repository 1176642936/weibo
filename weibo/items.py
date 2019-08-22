# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import  Item , Field


#用户信息列表
class User_Item(Item):
    #设置mongodb中的集合
    collection = 'users'
    id = Field()
    name = Field()
    avatar = Field()
    cover = Field()
    fans = Field()
    follows = Field()
    crawler_at = Field()
    fans_count = Field()
    follows_count = Field()

#关注和粉丝
class UserRalationItem(Item):
    collection = 'users'
    id = Field()
    fans = Field()
    follows = Field()


#微博数据
class WeiboItem(Item):
    collection = 'weibos'
    user = Field()
    id = Field()
    source = Field()
    attitudes = Field()
    comments = Field()
    text = Field()
    created_at = Field()
    crawler_at = Field()
