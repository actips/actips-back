class OJAdapterBase(object):
    # 匹配 OnlineJudgeSite 的 code
    code = None
    charset = 'utf8'
    homepage = None

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

    # def get_title_from_body(self, content):
    #     """ 编写规则从页面内容中解析出题目标题 """
    #     raise NotImplementedError
    #
    # def get_content_from_body(self, content):
    #     """ 编写规则从页面内容中解析出题目内容 """
    #     raise NotImplementedError

    # def get_input_sample_from_content(self, content):
    #     """ 编写规则从页面内容中解析出样例输入 """
    #     raise NotImplementedError
    #
    # def get_output_sample_from_content(self, content):
    #     """ 编写规则从页面内容中解析出样例输入 """
    #     raise NotImplementedError

    # def get_input_sample_from_content(self, content):
    #     """ 编写规则从页面内容中解析出样例输入 """
    #     raise NotImplementedError
    #
    # def get_output_sample_from_content(self, content):
    #     """ 编写规则从页面内容中解析出样例输入 """
    #     raise NotImplementedError

    def download_problem(self, num):
        """ 获取并返回一个问题对象 """
        raise NotImplementedError

    # def get_problem_supported_languages(self, problem):
    #     """ 获取某道题目支持的编程语言 """
    #     raise NotImplementedError

    # 用户档案部分
    def get_user_solved_problem_list(self):
        """ 获取用户已通过题目列表 """
        raise NotImplementedError

    def get_user_failed_problem_list(self):
        """ 获取用户未通过题目列表 """
        raise NotImplementedError

    def get_user_submission_list(self):
        """ 获取用户的提交列表 """
        raise NotImplementedError

    # 题目提交部分
    def get_platform_user_context(self):
        """ 获取平台官方代理用户的会话 """
        raise NotImplementedError

    def get_user_context_by_http_client(self, cookie, headers):
        """ 根据用户的 Cookie 和 Header 获取用户会话 """
        raise NotImplementedError

    def get_user_context_by_user_and_password(self, cookie, headers):
        """ 根据用户的 Cookie 和 Header 获取用户会话 """
        raise NotImplementedError

    def run_tests(self):
        """ 运行所有测试（实现类的所有 test 前缀都会被运行） """
