import json
from urllib.request import urlopen

from bs4 import BeautifulSoup


def request_text(url, charset='utf8'):
    """ 请求一个页面，返回用 BS4 解析之后的 DOM 对象 """
    # print('>>> request_text: {}'.format(url))
    resp = urlopen(url)
    body = resp.read().decode(charset)
    # print(body)
    return body


def request_dom(url, charset='utf8'):
    """ 请求一个页面，返回用 BS4 解析之后的 DOM 对象 """
    # print('>>> request_dom: {}'.format(url))
    body = request_text(url, charset)
    # print(body)
    return BeautifulSoup(body, 'lxml')


def request_json(url, charset='utf8'):
    """ 请求一个页面，返回用 json 解析之后的对象 """
    # print('>>> request_json: {}'.format(url))
    body = request_text(url, charset)
    # print(body)
    return json.loads(body)
