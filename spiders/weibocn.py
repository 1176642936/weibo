# -*- coding: utf-8 -*-
from scrapy import  Spider, Request
from  scrapy.http.response.html import HtmlResponse
import  json
from ..items import *
import  time
import   re


class WeiboSpider(Spider):
    name = 'weibocn'
    allowed_domains = ['m.weibo.cn']
    start_urls = ['6516891371']
    #手机版用户首页url
    user_url = 'https://m.weibo.cn/profile/info?uid={uid}'
    #用户动态首页url
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?containerid=107603{uid}'
    #用户关注url
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}'
    #用户粉丝url
    fans_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}'
    def start_requests(self):
        for uid in  self.start_urls:
            yield Request(self.user_url.format(uid=uid), callback=self.parse_user)

    def parse_user(self, response:HtmlResponse):
        '''
        开始解析第一批用户信息，获取uid，将uid传递至需要解析的用户：微博、关注、粉丝url中
        :param response: HtmlResponse
        :return:
        '''
        result = json.loads(response.text)
        User_info = result.get('data').get('user')
        # print(User_info)
        User_item = User_Item()
        if User_info:
            #形成key,value键值对，方便将页面中的信息提取至item中
            filed_map = {'id': 'id', 'name': 'screen_name', 'avatar': 'avatar_hd', 'cover': 'cover_image_phone',
                         'fans_count': 'followers_count',
                         'follows_count': 'follow_count'}
            for k, v in filed_map.items():
                if k == 'id':
                    #item存储需要字符串类型，在此提取时做类型转换
                    User_item[k] = str(User_info.get(v))
                    continue
                User_item[k] = User_info.get(v)
            yield User_item
            uid = User_info.get('id')
            ##依次开始解析
            #关注
            yield Request(url=self.follow_url.format(uid=uid), callback=self.parse_follows, meta={'uid':uid})
            # #粉丝
            yield Request(url=self.fans_url.format(uid=uid), callback=self.parse_fans, meta={'uid':uid})
            # # #微博
            yield Request(url=self.weibo_url.format(uid=uid), callback=self.parse_weibos, meta={'uid':uid})

    def parse_follows(self, response:HtmlResponse):
        '''
        解析用户关注对象
        :param response:
        :return:
        '''
        result = json.loads(response.text)
        print(response.url, '-'*30)
        #关注首页与其他页面在返回的数据中有所不同，故做分类判断
        page = re.search('page=(\d+)', response.url)
        i = 1
        if page:
            if int(page.group(1)) > 1 :
                i = 0
        if result.get('data').get('cards') and len(result.get('data').get('cards')[i].get('card_group')):
            print('-'*30)
            follows = result.get('data').get('cards')[i].get('card_group')
            #递归解析
            # for follow in follows :
            #     if follow.get('user'):
            #         uid = follow.get('user').get('id')
            #         yield Request(url=self.user_url.format(uid=uid), callback=self.parse_user)
            uid = response.meta.get('uid')
            follows = [{'id':follow.get('user').get('id'),'name':follow.get('user').get('screen_name')}
                       for follow in follows]
            user_ralation_item = UserRalationItem()
            user_ralation_item['id'] = str(uid)
            user_ralation_item['follows'] = follows
            user_ralation_item['fans'] = []
            print(dict(user_ralation_item))
            yield user_ralation_item
            #页面是ajax形式， 从前一页可以读取下一页的page信息
            page = result.get('data').get('cardlistInfo').get('page')
            if int(page) > 1:
                time.sleep(3)
                yield Request(url=self.follow_url.format(uid=uid) + '&page={}'.format(page),
                              callback=self.parse_follows, meta={'uid':uid})
    def parse_fans(self, response:HtmlResponse):
        '''
        解析粉丝
        :param response:
        :return:
        '''
        result = json.loads(response.text)
        print(response.url)
        if result.get('data').get('cards') and len(result.get('data').get('cards')[0].get('card_group')):
            follows = result.get('data').get('cards')[0].get('card_group')

            #递归解析
            # for follow in  follows:
            #     if follows.get('user'):
            #         uid = follow.get('user').get('id')
            #         yield Request(url=self.user_url.format(uid=uid), callback=self.parse_user)
            uid = response.meta.get('uid')
            fans = [{'id':follow.get('user').get('id'), 'name':follow.get('user').get('screen_name')} for follow in follows]
            user_ralation_item = UserRalationItem()
            user_ralation_item['id'] = str(uid)
            user_ralation_item['follows'] = []
            user_ralation_item['fans'] = fans
            print(dict(user_ralation_item))
            yield user_ralation_item

            #读取下一页信息
            since_id = result.get('data').get('cardlistInfo').get('since_id')
            if int(since_id) > 1:
                time.sleep(3)
                yield Request(url=self.fans_url.format(uid=uid) + '&since_id={}'.format(since_id),
                              callback=self.parse_fans, meta={'uid':uid})

    def parse_weibos(self, response:HtmlResponse):
        '''
        解析微博
        :param response:
        :return:
        '''
        result = json.loads(response.text)
        print(response.url)
        if result.get('data').get('cards') and  len(result.get('data').get('cards')):
            items = result.get('data').get('cards')
            field_map = {'id':'id','source':'source','attitudes':'attitudes_count', 'comments':'comments_count','text':'text','created_at':'created_at'}
            for  item in items:
                mblog = item.get('mblog')
                if mblog:
                    Weibo_item = WeiboItem()
                    for k, v in field_map.items():
                        Weibo_item[k] = mblog.get(v)
                    Weibo_item['user'] = response.meta.get('uid')
                    yield Weibo_item
            uid = response.meta.get('uid')
            page = result.get('data').get('cardlistInfo').get('page')
            if int(page) > 1:
                time.sleep(3)
                yield Request(url=self.weibo_url.format(uid=uid) + '&page={}'.format(page), callback=self.parse_weibos,
                              meta={'uid':uid})


