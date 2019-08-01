import json
import re

import requests
from bs4 import BeautifulSoup
from html2text import html2text

from ojadapter.entity.Problem import Problem
from ojadapter.entity.UserContext import UserContext
from ojadapter.entity.Submission import Submission
from ...utils import request_dom, request_text, request_json, request_raw
from ..OJAdapterBase import OJAdapterBase, OJAdapterException
from urllib.parse import urljoin


class OJAdapterCodeforces(OJAdapterBase):
    # TODO: 要添加 Mathjax 对嵌入的 Tex 的支持
    # TODO: pdf 类型题目依然是一个体验不好的环节
    # TODO: 登录和交题、下载提交记录模块还没有完成
    # OSError: [Errno 18] Invalid cross-device link: '/tmp/m4o5v_pk' -> '/var/app/media/oj/CF/images/1e8f542ba3440a36164e78ab61f6806f'

    code = 'CF'
    homepage = r'https://codeforces.com'

    # platform_username = 'actips.org'
    # platform_password = 'Actips@2019'

    # API key-secret
    platform_username = 'dd352833dcf086818aaa59db9e3914ae963834f7'
    platform_password = 'db6af912eab8c288e4d17b87cd29c48be2828663'

    def get_supported_languages(self):
        # TODO: 这个 id 并不是连续的，要遍历所有Problem统计一下有没有遗漏
        # TODO: 在 Codeforces 提交列表里面出来的 label 值还要重新测试一遍
        return [
            dict(id=2, label='MS C++', language=Submission.LANGUAGE_CPP, version='Microsoft Visual C++ 2010'),
            dict(id=3, language=Submission.LANGUAGE_DELPHI, version='Delphi 7'),
            dict(id=4, language=Submission.LANGUAGE_PASCAL, version='Free Pascal 3.0.2'),
            dict(id=6, language=Submission.LANGUAGE_PHP, version='PHP 7.2.13'),
            dict(id=7, language=Submission.LANGUAGE_PYTHON2, version='Python 2.7.15'),
            dict(id=8, language=Submission.LANGUAGE_RUBY, version='Ruby 2.0.0p645'),
            dict(id=9, language=Submission.LANGUAGE_CSHARP, version='C# Mono 5.18'),
            dict(id=12, language=Submission.LANGUAGE_HASKELL, version='Haskell GHC 8.6.3'),
            dict(id=13, language=Submission.LANGUAGE_PERL, version='Perl 5.20.1'),
            dict(id=19, language=Submission.LANGUAGE_OCAML, version='OCaml 4.02.1'),
            dict(id=20, language=Submission.LANGUAGE_SCALA, version='Scala 2.12.8'),
            dict(id=28, language=Submission.LANGUAGE_D, version='D DMD32 v2.086.0'),
            dict(id=31, language=Submission.LANGUAGE_PYTHON3, version='Python 3.7.2'),
            dict(id=32, language=Submission.LANGUAGE_GO, version='Go 1.12.6'),
            dict(id=34, language=Submission.LANGUAGE_JAVASCRIPT, version='JavaScript V8 4.8.0'),
            dict(id=36, language=Submission.LANGUAGE_JAVA, version='Java 1.8.0_162'),
            dict(id=40, language=Submission.LANGUAGE_PYTHON2, version='PyPy 2.7 (7.1.1)'),
            dict(id=41, language=Submission.LANGUAGE_PYTHON3, version='PyPy 3.6 (7.1.1)'),
            dict(id=42, language=Submission.LANGUAGE_CPP, version='GNU G++11 5.1.0'),
            dict(id=43, language=Submission.LANGUAGE_C, version='GNU GCC C11 5.1.0'),
            dict(id=48, language=Submission.LANGUAGE_KOTLIN, version='Kotlin 1.3.10'),
            dict(id=49, language=Submission.LANGUAGE_RUST, version='Rust 1.35.0'),
            dict(id=50, label='GNU C++14', language=Submission.LANGUAGE_CPP, version='GNU G++14 6.4.0'),
            dict(id=51, language=Submission.LANGUAGE_PASCAL, version='PascalABC.NET 3.4.2'),
            dict(id=52, language=Submission.LANGUAGE_CLANG, version='Clang++17 Diagnostics'),
            dict(id=54, label='GNU C++17', language=Submission.LANGUAGE_CPP, version='GNU G++17 7.3.0'),
            dict(id=55, language=Submission.LANGUAGE_NODEJS, version='Node.js 9.4.0'),
            dict(id=59, label='MS C++', language=Submission.LANGUAGE_CPP, version='Microsoft Visual C++ 2017')
        ]

    def get_all_contest_numbers(self):
        # http://codeforces.com/api/contest.list?gym=true
        data = request_json(urljoin(self.homepage, '/api/contest.list'), self.charset)
        # 接口是按照从新到旧返回的，倒过来
        return [x.get('id') for x in data.get('result')][::-1]

    def get_all_problem_numbers(self):
        data = request_json(urljoin(self.homepage, '/api/problemset.problems'), self.charset)
        # 接口是按照从新到旧返回的，倒过来
        return ['{contestId}{index}'.format(**x) for x in data.get('result').get('problems')][::-1]

    def _get_contest_and_index_from_problem_id(self, problem_id):
        if re.match(r'921\d\d', problem_id):
            # 921 号比赛的题目编号不是 ABCDE，是 01-14，大爷的特别关照
            contest_id = 921
            index = problem_id[3:]
        else:
            # 正常情况
            contest_id, index = re.match(r'(\d+)(.+)', problem_id).groups()
        return contest_id, index

    def get_problem_url(self, problem_id, contest_id=None):
        return urljoin(self.homepage, '/contest/{}/problem/{}'.format(
            *self._get_contest_and_index_from_problem_id(problem_id)))

    def download_problem(self, problem_id, contest_id=None):
        """ 获取并返回一个问题对象 """
        # Codeforces 失败的奇葩之处目前发现这几点：
        # 1 是 pdf 的题目信息，2 是 鹅语题目，3 是非字母的题目号（921比赛）
        url = self.get_problem_url(problem_id, contest_id)
        # Codeforces 的 contest_id 是包含在 problem_id 里面的
        contest_id, index = self._get_contest_and_index_from_problem_id(problem_id)
        resp = request_raw(url)
        if resp.headers.get('Content-Type').startswith('application/pdf'):
            pdf_path = self.download_file(url, 'pdf')
            # if True:
            #     pdf_path = '/media/fuck'
            # 其他的信息要从比赛页面的列表中获取了
            dom = request_dom(urljoin(self.homepage, '/contest/' + contest_id))
            title = ''
            time_limit = 0
            memory_limit = 0
            for tr in dom.select('table.problems tr'):
                if len(tr.select('td')) < 2:
                    continue
                td = tr.select('td')[0]
                if td.text.strip() == index:
                    td = tr.select('td')[1]
                    title = td.select_one('a').text
                    time_limit, memory_limit = re.search(r'([\d.]+)\s+s,\s+(\d+)\s+MB',
                                                         td.select_one('.notice').text).groups()
            problem = self.parse_problem('''
            <div class="problem-statement">
                <div class="header">
                    <div class="title">{title}</div>
                    <div class="time-limit">time limit per test{time_limit} seconds</div>
                    <div class="memory-limit">memory limit per test{memory_limit} megabytes</div>
                </div>
                <div>
                    <p>See the problem description in the 
                    <a target="_blank" href="{pdf_path}">pdf</a> link.</p>
                    <p>
                        <!-- markdown 之后会被吃掉，后面再想办法 -->
                        <object data="{pdf_path}" type="application/pdf">
                            <embed src="{pdf_path}" type="application/pdf" />
                            <iframe src="{pdf_path}"></iframe>
                        </object>
                    </p>
                </div>
            </div>
            '''.format(title=title, pdf_path=pdf_path, time_limit=time_limit, memory_limit=memory_limit))
            # TODO: 啊啊啊，pdf 啊！！！！不知如何是好！！！！
            # raise OJAdapterException('pdf 没招了', 9999)
        else:
            html = resp.content.decode(self.charset)
            problem = self.parse_problem(html)
        problem.id = problem_id
        problem.contest_id = contest_id
        return problem

    def parse_problem(self, body):
        # 构造空白问题对象
        problem = Problem()
        problem.input_samples = []
        problem.output_samples = []
        problem.extra_info = dict()
        # 开始处理
        dom = BeautifulSoup(body, 'lxml')
        # Codeforces 专有，转换加粗的标签
        for el in dom.select('.tex-font-style-bf'):
            el.name = 'strong'  # to markdown **<content>**
        for el in dom.select('.tex-font-style-tt'):
            el.name = 'code'  # to markdown `<content>`
        # 解析标题
        problem.title = re.sub('^[^.]+\.\s+', '', dom.select('div.title')[0].text.strip())
        # 解析时间限制、Special Judge
        row_time_limit = dom.select_one('.time-limit').text
        row_memory_limit = dom.select_one('.memory-limit').text
        # 转化为毫秒
        problem.time_limit = \
            int(float(re.findall(
                r'(?:time limit per test|ограничение по времени на тест)\s*([\d.]+)\s+'
                r'(?:seconds?|секунда|секунды)', row_time_limit)[0]) * 1000)
        # 转化为 KB
        problem.memory_limit = \
            int(re.findall(
                r'(?:memory limit per test|ограничение по памяти на тест)\s*(\d+)\s+'
                r'(?:megabytes|мегабайт)', row_memory_limit)[0]) * 1024
        # Codefoces 没有显式声明一个题目是否为 Special Judge
        problem.is_special_judge = False
        # 解析正文内容
        problem_content = dom.select_one('.problem-statement')
        problem_content.select_one('.header').decompose()

        input_specification = problem_content.select_one('.input-specification')
        if input_specification:
            input_specification.select_one('.section-title').decompose()
            problem.input_specification = \
                self.sanitize_content(input_specification.decode_contents())
            input_specification.decompose()

        output_specification = problem_content.select_one('.output-specification')
        if output_specification:
            output_specification.select_one('.section-title').decompose()
            problem.output_specification = \
                self.sanitize_content(output_specification.decode_contents())
            output_specification.decompose()

        note = problem_content.select_one('.note')
        if note:
            note.select_one('.section-title').decompose()
            problem.extra_description = \
                self.sanitize_content(note.decode_contents())
            note.decompose()

        sample_tests = problem_content.select_one('.sample-tests')
        if sample_tests:
            from bs4.element import Tag
            for el in sample_tests.select('.input'):
                pre = el.select_one('pre')
                # 输出的时候有时会是 <br>，需要过滤掉
                problem.input_samples.append(
                    '\n'.join([line for line in pre.contents if not isinstance(line, Tag)]).strip('\n'))
            for el in sample_tests.select('.output'):
                pre = el.select_one('pre')
                # 输出的时候有时会是 <br>，需要过滤掉
                problem.output_samples.append(
                    '\n'.join([line for line in pre.contents if not isinstance(line, Tag)]).strip('\n'))
            sample_tests.decompose()

        problem.description = self.sanitize_content(problem_content.decode_contents())

        # 解析 problem tags
        for el in dom.select('.sidebox'):
            # print(el)
            caption = el.select_one('.caption.titled')
            if caption and 'Problem tags' in caption.text:
                problem.extra_info['tags'] = ','.join([box.text.strip() for box in el.select('.tag-box')])
        problem.extra_info = json.dumps(problem.extra_info)

        # problem.print()
        return problem

    # def get_user_context_by_user_and_password(self, username, password):
    #     context = UserContext()
    #     # from requests.cookies import cookiejar_from_dict
    #     # cookie_str = 'JSESSIONID=F2D80B8A1EB6F01ABBC3DB6E93D6B1B8-n1'
    #     #              # 'lastOnlineTimeUpdaterInvocation=1564554364726; __utmc=71512449; __utmz=71512449.1556204443.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _ym_uid=1556204446401314995; _ym_d=1556204446; 39ce7=CF9iRVAW; __utma=71512449.11295113.1556204443.1564543936.1564548953.9; evercookie_etag=aljyst33rolg7nqnlh; evercookie_cache=aljyst33rolg7nqnlh; evercookie_png=aljyst33rolg7nqnlh; 70a7c28f3de=aljyst33rolg7nqnlh; X-User=; X-User-Sha1=a9ecea30205efe270872f6a64711bf3a9b49e128; lastOnlineTimeUpdaterInvocation=1564551615687; __utmt=1; __utmb=71512449.37.10.1564548953'
    #     # cookie_dict = dict()
    #     # for p in cookie_str.split('; '):
    #     #     k, v = re.match('^([^=]+)=(.*)$', p).groups()
    #     #     cookie_dict[k] = v
    #     # print(cookie_dict)
    #     # context.session.cookies = cookiejar_from_dict(cookie_dict)
    #     #
    #     # resp = context.session.get(urljoin(self.homepage, '/settings/api'))
    #     # print(resp.content.decode())
    #     # print('fish_ball' in resp.content.decode())
    #     # return
    #
    #     resp = context.session.get(url=urljoin(self.homepage, '/enter'))
    #     resp = context.session.get(url=urljoin(self.homepage, '/enter'))
    #     body = resp.content.decode()
    #     csrftoken = re.search(r'<meta name="X-Csrf-Token" content="([0-9a-f]+)"/>', body).groups()[0]
    #     print(context.session.cookies)
    #     from random import random
    #     _ftaa = ''.join(str(int(random() * 10)) for x in range(18))
    #     print(_ftaa)
    #     # print(body)
    #     _ftaa = re.search(r'window._ftaa = "([0-9a-z]+)"', body).groups()[0]
    #     _bfaa = re.search(r'window._bfaa = "([0-9a-z]+)"', body).groups()[0]
    #     print(csrftoken, _ftaa, _bfaa)
    #
    #     resp = context.session.post(
    #         url=urljoin(self.homepage, '/enter'),
    #         data=dict(
    #             csrf_token=csrftoken,
    #             action='enter',
    #             ftaa=_ftaa,
    #             bfaa=_bfaa,
    #             handleOrEmail=username,
    #             password=password,
    #             _tta='726',
    #         ),
    #     )
    #     if resp.status_code >= 400:
    #         return None
    #     # context.save()
    #     return context
    #
    # def check_context_validity(self, context):
    #     resp = context.session.get(urljoin(self.homepage, 'onlinejudge'))
    #     content = resp.content.decode(self.charset)
    #     groups = re.findall(r'showUserStatus\.do\?userId=(\d+)', content)
    #     return bool(groups)
    #
    # def get_user_solved_problem_list(self, context):
    #     """ 获取用户已通过题目列表 """
    #     data = context.session.get(urljoin(self.homepage, '/api/problemset.problems'))
    #     print(data.get('result').get('problems'))
    #     return sorted('{contestId}{index}'.format(**x) for x in data.get('result').get('problems'))
    #     return []
    #     # 获取用户 id
    #     resp = context.session.get(urljoin(self.homepage, 'onlinejudge'))
    #     content = resp.content.decode(self.charset)
    #     # print(content)
    #     groups = re.findall(r'showUserStatus\.do\?userId=(\d+)', content)
    #     # print(groups)
    #     user_id = groups[0]
    #     # 获取状态页面
    #     resp = context.session.get(urljoin(
    #         self.homepage, 'onlinejudge/showUserStatus.do?userId={}'.format(user_id)
    #     ))
    #     problem_ids = re.findall(r'href="/onlinejudge/showProblem\.do\?problemCode=(\d+)"',
    #                              resp.content.decode(self.charset))
    #     return problem_ids
    #
    # def get_user_failed_problem_list(self, context):
    #     """ 获取用户未通过题目列表 """
    #     # 可以后面翻一下提交记录
    #     # ZOJ 并没有列出这个信息
    #     return []
    #
    # def _parse_submission_row(self, context, row):
    #     status_map = {
    #         'Accepted': Submission.RESULT_ACCEPTED,
    #         'Presentation Error': Submission.RESULT_PRESENTATION_ERROR,
    #         'Wrong Answer': Submission.RESULT_WRONG_ANSWER,
    #         'Time Limit Exceeded': Submission.RESULT_TIME_LIMIT_EXCEED,
    #         'Memory Limit Exceeded': Submission.RESULT_MEMORY_LIMIT_EXCEED,
    #         'Segmentation Fault': Submission.RESULT_SEGMENT_FAULT,
    #         'Non-zero Exit Code': Submission.RESULT_NON_ZERO_EXIT_CODE,
    #         'Floating Point Error': Submission.RESULT_FLOAT_POINT_ERROR,
    #         'Compilation Error': Submission.RESULT_COMPILATION_ERROR,
    #         'Output Limit Exceeded': Submission.RESULT_OUTPUT_LIMIT_EXCEED,
    #         'Runtime Error': Submission.RESULT_RUNTIME_ERROR,
    #     }
    #     language_map = {
    #         'C': Submission.LANGUAGE_C,
    #         'C++': Submission.LANGUAGE_GPP,
    #         'FPC': Submission.LANGUAGE_PASCAL,
    #         'Java': Submission.LANGUAGE_JAVA,
    #         'Python': Submission.LANGUAGE_PYTHON2,
    #         'Perl': Submission.LANGUAGE_PERL,
    #         'Scheme': Submission.LANGUAGE_SCHEME,
    #         'PHP': Submission.LANGUAGE_PHP,
    #         'C++11': Submission.LANGUAGE_CPP11,
    #     }
    #     submission_id = row.select_one('.runId').text
    #     # print(row.select_one('.runJudgeStatus').text.strip())
    #     submission = Submission(
    #         id=submission_id,
    #         submit_time=row.select_one('.runSubmitTime').text,
    #         result=status_map.get(row.select_one('.runJudgeStatus').text.strip()) or '',
    #         problem_id=row.select_one('.runProblemId').text,
    #         language=language_map.get(row.select_one('.runLanguage').text) or '',
    #         run_time=int(row.select_one('.runTime').text or -1),
    #         run_memory=int(row.select_one('.runMemory').text or -1),
    #     )
    #     # print(row)
    #     code = context.session \
    #         .get(urljoin(self.homepage, row.select_one('.runLanguage a').attrs.get('href'))) \
    #         .content.decode(self.charset)
    #     submission.code = code
    #     return submission
    #
    # def _query_submission(self, context, handle=None, first_id=-1, last_id=-1, id_start='', id_end=''):
    #     handle = handle or context.session.cookies['oj_handle']
    #     resp = context.session.get(
    #         url=urljoin(
    #             self.homepage,
    #             '/onlinejudge/showRuns.do'
    #             '?contestId=1&search=true'
    #             '&firstId={}&lastId={}&problemCode='
    #             '&handle={}&idStart={}&idEnd={}'.format(
    #                 first_id, last_id, handle, id_start, id_end)
    #         )
    #     )
    #     content = resp.content.decode(self.charset)
    #     soup = BeautifulSoup(content, 'lxml')
    #     rows = soup.select('table.list tr')[1:]
    #     # next page link
    #     groups = re.findall(r'JavaScript: goNext\((\d+)\);', content)
    #     next_id = groups[0] if groups else None
    #     return rows, next_id
    #
    # # def get_user_submission(self, context, submission_id):
    # #     """ 获取用户的提交列表 """
    # #     results = []
    # #     next_id = -1
    # #     # TODO: excludes 尚未实现
    # #     while next_id:
    # #         rows, next_id = self._query_submission(context, last_id=next_id)
    # #         for row in rows[1:]:
    # #             submission = self._parse_submission_row(context, row)
    # #             results.append(submission)
    # #             # print(submission.__dict__)
    # #     return results
    #
    # def get_user_submission_list(self, context, excludes=()):
    #     """ 获取用户的提交列表
    #     TODO: 这个方法太重了，一跑起来没完没了，后面考虑一下优化的问题，将抓取任务切碎
    #     """
    #     results = []
    #     next_id = -1
    #     # TODO: excludes 尚未实现
    #     while next_id:
    #         rows, next_id = self._query_submission(context, last_id=next_id)
    #         for row in rows[1:]:
    #             submission = self._parse_submission_row(context, row)
    #             # print(submission.id, submission.submit_time)
    #             results.append(submission)
    #             # print(submission.__dict__)
    #     return results
    #
    # def submit_problem(self, context, problem_id, language, code, contest_id=None):
    #     # 实际提交的 problemID 和题目的 problem_id 不一致，需要先抓过来转换一下
    #     resp = context.session.get(urljoin(
    #         self.homepage,
    #         r'/onlinejudge/showProblem.do?problemCode={}'.format(problem_id)))
    #     print('>>> origin problem_id = {}'.format(problem_id))
    #     problem_id = re.findall(r'/onlinejudge/submit\.do\?problemId=(\d+)',
    #                             resp.content.decode(self.charset))[0]
    #     print('>>> actual problem_id = {}'.format(problem_id))
    #     # 映射 language_id
    #     from ojadapter.entity.Submission import Submission
    #     language_id = {
    #         Submission.LANGUAGE_C: 1,
    #         Submission.LANGUAGE_GPP: 2,
    #         Submission.LANGUAGE_PASCAL: 3,
    #         Submission.LANGUAGE_JAVA: 4,
    #         Submission.LANGUAGE_PYTHON2: 5,
    #         Submission.LANGUAGE_PERL: 6,
    #         Submission.LANGUAGE_SCHEME: 7,
    #         Submission.LANGUAGE_PHP: 8,
    #         Submission.LANGUAGE_CPP11: 9,
    #     }.get(language)
    #     # 提交代码
    #     resp = context.session.post(
    #         url=urljoin(self.homepage, '/onlinejudge/submit.do'),
    #         data=dict(
    #             problemId=problem_id,
    #             languageId=language_id,
    #             source=code,
    #         ),
    #     )
    #     soup = BeautifulSoup(resp.content.decode(self.charset), 'lxml')
    #     # print(soup)
    #     submission_id = soup.select_one(r'#content_body font[color="red"]').text
    #     print('>>> submission_id: {}'.format(submission_id))
    #     # 获取结果
    #     retry = 10
    #     while True:
    #         rows, next_id = self._query_submission(
    #             context, id_end=submission_id, id_start=submission_id)
    #         # print(rows, next_id)
    #         # print(rows[0].select_one('.judgeReplyOther').text.strip())
    #         submission = self._parse_submission_row(context, rows[0])
    #         retry -= 1
    #         if submission.result or not retry:
    #             break
    #         from time import sleep
    #         sleep(11 - retry)
    #     return submission
