import json
from urllib.request import urlopen

from bs4 import BeautifulSoup

from ojadapter.entity.UserContext import UserContext


def get_proxy_from_pool():
    # TODO: 我好懒，后面代理池地址移到配置里面吧
    # TODO: 暂且放弃这个实现，因为没有好的 https 代理源
    import requests
    resp = requests.get('https://proxy.easecloud.cn/get')
    return resp.content.decode()


def request_raw(url, context=None, use_proxy=False):
    context = context or UserContext()
    return context.session.get(url, timeout=120)


def request_text(url, charset='utf8', context=None, use_proxy=False):
    """ 请求一个页面，返回用 BS4 解析之后的 DOM 对象 """
    # print('>>> request_text: {}'.format(url))
    resp = request_raw(url, context, use_proxy)
    body = resp.content.decode(charset, errors='ignore')
    # print(body)
    return body


def request_dom(url, charset='utf8', context=None, use_proxy=False):
    """ 请求一个页面，返回用 BS4 解析之后的 DOM 对象 """
    # print('>>> request_dom: {}'.format(url))
    body = request_text(url, charset, context, use_proxy)
    # print(body)
    return BeautifulSoup(body, 'lxml')


def request_json(url, charset='utf8', context=None, use_proxy=False):
    """ 请求一个页面，返回用 json 解析之后的对象 """
    # print('>>> request_json: {}'.format(url))
    body = request_text(url, charset, context, use_proxy)
    # print(body)
    return json.loads(body)
