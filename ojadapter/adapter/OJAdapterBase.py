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
        """ 获取OJ支持的编程语言 """
        raise NotImplementedError

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
        return self.get_supported_languages()

    def submit_problem(self, context, problem_id, language, code, contest_id=None):
        """ 提交一个题目
        :param context: 当前的会话
        :param problem_id: 题目编号
        :param language: 提交的编程语言，采用内部的 Submission.LANGUAGE_CHOICES 取值
        :param code: 代码内容
        :param contest_id: 提交的比赛ID（如果有）
        :return:
        """
        raise NotImplementedError
