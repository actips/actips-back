from ojadapter.entity.Submission import Submission
from ojadapter.entity.UserContext import UserContext


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

    def parse_problem(self, body):
        """ 通过题目内容解析出题目的内容
        :param body: 请求问题链接获取的响应内容字符串（Unicode）
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
        html = request_text(self.get_problem_url(problem_id, contest_id))
        problem = self.parse_problem(html)
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
