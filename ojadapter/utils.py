import json
from urllib.request import urlopen

from bs4 import BeautifulSoup

from ojadapter.entity.UserContext import UserContext


def request_text(url, charset='utf8', context=None):
    """ 请求一个页面，返回用 BS4 解析之后的 DOM 对象 """
    # print('>>> request_text: {}'.format(url))
    context = context or UserContext()
    resp = context.session.get(url, timeout=120)
    body = resp.content.decode(charset)
    # print(body)
    return body


def request_dom(url, charset='utf8', context=None):
    """ 请求一个页面，返回用 BS4 解析之后的 DOM 对象 """
    # print('>>> request_dom: {}'.format(url))
    body = request_text(url, charset, context)
    # print(body)
    return BeautifulSoup(body, 'lxml')


def request_json(url, charset='utf8', context=None):
    """ 请求一个页面，返回用 json 解析之后的对象 """
    # print('>>> request_json: {}'.format(url))
    body = request_text(url, charset, context)
    # print(body)
    return json.loads(body)
