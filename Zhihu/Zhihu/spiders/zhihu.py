# -*- coding: utf-8 -*-
import json

import scrapy

from Zhihu.items import UserItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'
    start_user = 'excited-vczh'
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield scrapy.Request(self.user_url.format(user=self.start_user, include=self.user_query), callback=self.parse_user)
        yield scrapy.Request(self.follows_url.format(user=self.start_user, include=self.follows_query, offset=0, limit=20), callback=self.parse_follows)
        yield scrapy.Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20),
            callback=self.parse_followers)

    def parse_user(self, response):
        '''用户信息'''
        # print(response.url, '>>>> ')
        result = json.loads(response.text)
        print(result)
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        yield scrapy.Request(url=self.follows_url.format(user=result.get('url_token'),include=self.follows_query, limit=20,offset=0),callback=self.parse_follows)
        yield scrapy.Request(url=self.followers_url.format(user=result.get('url_token'), include=self.followers_query, limit=20, offset=0),
            callback=self.parse_followers)

    def parse_follows(self,response):
        '''关注列表'''
        result = json.loads(response.text)
        if 'data' in result.keys():
            for result in result.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'),include=self.user_query), self.parse_user)
        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:
            next_page = result.get('paging').get('next')
            yield scrapy.Request(next_page,self.parse_follows)

    def parse_followers(self,response):
        '''关注者（粉丝）列表'''
        result = json.loads(response.text)
        if 'data' in result.keys():
            for result in result.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'), include=self.user_query), self.parse_user)
        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:
            next_page = result.get('paging').get('next')
            yield scrapy.Request(next_page,self.parse_followers)