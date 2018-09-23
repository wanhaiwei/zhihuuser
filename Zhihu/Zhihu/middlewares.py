import requests
import random
from Zhihu.settings import *


class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        user_agent = random.choice(USER_AGENTS)
        request.headers['User-Agent'] = user_agent


class ProxyMiddleware(object):
    def __init__(self):
        self.proxy_pool_url = 'http://127.0.0.1:5000/get'

    def process_request(self, request, spider):
        '''对request对象加上proxy'''
        proxy = self.get_proxy()
        print("this is request ip:" + proxy)
        request.meta['proxy'] = proxy

    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            proxy = self.get_proxy()
            print("this is response ip:" + proxy)
            # 对当前request加上代理
            request.meta['proxy'] = proxy
            return request
        return response

    def get_proxy(self):
        try:
            response = requests.get(self.proxy_pool_url)
            if response.status_code == 200:
                return response.text
            return None
        except ConnectionError:
            return None
