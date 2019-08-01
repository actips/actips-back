import os.path
import tempfile
import hashlib
from urllib.parse import urljoin

from ojadapter.entity.Submission import Submission
from ojadapter.entity.UserContext import UserContext


class OJAdapterException(Exception):
    def __init__(self, msg='', code=0):
        self.msg = msg
        self.code = code

    def __str__(self):
        return '[{}] {}'.format(self.code, self.msg)


class OJAdapterBase(object):
    """ OJ适配器类

    每个OJ各自实现一个子类以实现功能对接

    !!! 重要的事情说三遍 !!!

    一定要完整编写单元测试！
    一定要完整编写单元测试！
    一定要完整编写单元测试！
    """
    # 匹配 OnlineJudgeSite 的 code
    code = None
    charset = 'utf8'
    homepage = None

    # 平台登录OJ用的账户密码，下面这个是默认注册形式
    platform_username = 'actips'
    platform_password = 'Actips@2019'

    # 工具方法

    def download_file(self, url, folder, current_url=''):
        """ 下载一个 url 的文件，放到指定的 media 目录，文件名
        :param url: 下载的 URL 链接
        :param folder: /media/oj/<OJ_CODE>/ 下的子目录名
        :param current_url: 当前页面的路径（缺省为 homepage 的设定，用于计算图片路径）
        :return: 返回 /media 开头的路径
        """
        origin_url = url
        # print(url, folder, current_url)
        if url.startswith('/'):
            url = urljoin(current_url or self.homepage, url)
        elif url.startswith('http'):
            pass
        elif url.startswith('data:image'):
            # TODO: 解决 base64 类型的抓取问题
            raise NotImplementedError('base64 类图片处理尚未实现')
        else:
            # 相对路径
            if not current_url:
                raise NotImplementedError('相对路径未提供当前页面路径')
            url = urljoin(current_url, url)
        # 写入目标地址
        base_path = '/media/oj/' + self.code + '/' + folder + '/'
        file_path = os.path.abspath(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), '../..' + base_path))
        os.makedirs(file_path, 0o755, exist_ok=True)
        # 下载到临时文件
        # https://stackoverflow.com/a/26541521/2544762
        temp_file = os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()))
        from urllib.request import urlretrieve
        from urllib.error import HTTPError
        try:
            urlretrieve(url, temp_file)
        except HTTPError:
            print('HTTPError', url)
            return '/media/images/no-pic.png'
        except Exception as e:
            print(e, url)
            return origin_url
        # 计算图片文件的 md5 checksum
        # https://stackoverflow.com/a/3431838/2544762
        hash_md5 = hashlib.md5()
        with open(temp_file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        checksum = hash_md5.hexdigest()
        import shutil
        shutil.move(temp_file, os.path.join(file_path, checksum))
        return os.path.join(base_path, checksum)

    def sanitize_markdown(self, content, current_url=''):
        """ 将 content 从 markdown 整理内容
        并且将图片自动转储再添加引用
        :param content: 传入的原始 html
        :param current_url: 当前页面的路径（缺省为 homepage 的设定，用于计算图片路径）
        :return: 返回 markdown 纯文本字符串
        """
        import re
        # print(content)

        def replace_img_src(match):
            img_url, = match.groups()
            match = match.group()
            # print(img_url, match)
            return match.replace(img_url, self.download_file(img_url, 'images', current_url))

        result = re.sub(r'!\[(?:\\\]|[^]])*\]\(((?:\\\)|[^)])+)\)', replace_img_src, content)
        return result

    def sanitize_html(self, content, current_url=''):
        """ 将 content 从 html 转为 markdown 并且整理内容
        并且将图片自动转储再添加引用
        :param content: 传入的原始 html
        :param current_url: 当前页面的路径（缺省为 homepage 的设定，用于计算图片路径）
        :return: 返回 markdown 纯文本字符串
        """
        from bs4 import BeautifulSoup
        from html2text import html2text

        dom = BeautifulSoup(content, 'lxml')
        for img in dom.select('img'):
            # 整理图片文件绝对路径
            img['src'] = self.download_file(img['src'], 'images', current_url)

        return html2text(dom.decode_contents(), bodywidth=0).strip()

    # OJ整站配置获取部分

    def get_supported_languages(self):
        """ 获取OJ支持的编程语言，返回列表
        每个语言为一个字典，包含如下信息：
        id(语言编号), language(语言枚举值), version(版本字符串), label(显示的语言值)
        以 ZOJ 为例：
        return [
            dict(id=1, label='C', language=Submission.LANGUAGE_C, version='gcc 4.7.2'),
            dict(id=2, label='C++', language=Submission.LANGUAGE_CPP, version='g++ 4.7.2'),
            dict(id=3, label='FPC', language=Submission.LANGUAGE_FPC, version='fpc 2.6.0'),
            dict(id=4, label='Java', language=Submission.LANGUAGE_JAVA, version='java 1.7.0'),
            dict(id=5, label='Python', language=Submission.LANGUAGE_PYTHON2, version='Python 2.7.3'),
            dict(id=6, label='Perl', language=Submission.LANGUAGE_PERL, version='Perl 5.14.2'),
            dict(id=7, label='Scheme', language=Submission.LANGUAGE_SCHEME, version='Guile 1.8.8'),
            dict(id=8, label='PHP', language=Submission.LANGUAGE_PHP, version='PHP 5.4.4'),
            dict(id=9, label='C++11', language=Submission.LANGUAGE_CPP, version='g++ 4.7.2'),
        ]
        注意
        """
        raise NotImplementedError

    def get_language_by_id(self, id):
        for lang in self.get_supported_languages():
            if id and str(lang.get('id')) == str(id):
                return lang
        return None

    def get_language_id_by(self, key, value):
        """ 通过指定的键值获取 language id
        :param key:
        :param value:
        :return:
        """
        for lang in self.get_supported_languages():
            if lang.get(key) == value:
                return lang.get('id')
        return None

    def get_language_id_by_label(self, value):
        return self.get_language_id_by('label', value)

    def get_language_id_by_language(self, value):
        return self.get_language_id_by('language', value)

    # 比赛内容抓取部分

    def get_all_contest_numbers(self):
        """ 获取所有的比赛编号 """
        raise NotImplementedError

    # 题目内容抓取部分

    def get_all_problem_numbers(self):
        """ 获取所有的问题编号 """
        raise NotImplementedError

    def get_problem_url(self, problem_id, contest_id=None):
        """ 根据题号获取问题链接
        :param problem_id: 问题编号
        :param contest_id: 如果问题属于某个内部比赛，补充输入比赛编号
        :return:
        """
        raise NotImplementedError

    def parse_problem(self, body, current_url=''):
        """ 通过题目内容解析出题目的内容
        :param body: 请求问题链接获取的响应内容字符串（Unicode）
        :param current_url: 当前题目所在页面链接，用于计算资源相对路径
        :return:
        """
        raise NotImplementedError

    def get_platform_user_context(self):
        """ 获取平台官方代理用户的会话 """
        return self.get_user_context_by_user_and_password(
            self.platform_username,
            self.platform_password,
        )

    def get_user_context_by_http_client(self, cookies, headers):
        """ 根据用户的 Cookie 和 Header 获取用户会话 """
        context = UserContext()
        from requests.cookies import cookiejar_from_dict
        context.session.cookies = cookiejar_from_dict(cookies)
        context.session.headers = headers
        # context.save()
        return context

    def get_user_context_by_user_and_password(self, username, password):
        """ 根据用户的 Cookie 和 Header 获取用户会话 """
        raise NotImplementedError

    # 用户档案部分
    def get_user_solved_problem_list(self, context):
        """ 获取用户已通过题目列表 """
        raise NotImplementedError

    def get_user_failed_problem_list(self, context):
        """ 获取用户未通过题目列表 """
        raise NotImplementedError

    def get_user_submission_list(self, context):
        """ 获取用户的提交列表 """
        raise NotImplementedError

    def check_context_validity(self, context):
        """ 检测用户会话是否依然有效
        :param context: UserContext 对象
        :return:
        """
        raise NotImplementedError

    def download_problem(self, problem_id, contest_id=None):
        """ 获取并返回一个问题对象 """
        from ..utils import request_text
        url = self.get_problem_url(problem_id, contest_id)
        html = request_text(url)
        problem = self.parse_problem(html, url)
        problem.id = problem_id
        problem.contest_id = contest_id
        return problem

    def get_problem_supported_languages(self, problem):
        """ 获取某道题目支持的编程语言 """
        return problem.get_supported_languages()

    def submit_problem(self, context, problem_id, language_id, code, contest_id=None):
        """ 提交一个题目
        :param context: 当前的会话
        :param problem_id: 题目编号
        :param language_id: 提交的编程语言编号，采用 OJ 内部的语言 id
        :param code: 代码内容
        :param contest_id: 提交的比赛ID（如果有）
        :return:
        """
        raise NotImplementedError
