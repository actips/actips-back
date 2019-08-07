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


class OJAdapterHDOJ(OJAdapterBase):
    """
    """

    name = '杭电OJ'
    code = 'HDOJ'
    charset = 'gbk'
    homepage = r'http://acm.hdu.edu.cn'
    platform_username = 'actips'
    platform_password = 'Actips@2019'
    platform_email = 'admin@actips.org'

    def get_supported_languages(self):
        return [
            dict(id=0, label='G++', language=Submission.LANGUAGE_CPP, version=''),
            dict(id=1, label='GCC', language=Submission.LANGUAGE_C, version=''),
            dict(id=2, label='C++', language=Submission.LANGUAGE_CPP, version=''),
            dict(id=3, label='C', language=Submission.LANGUAGE_C, version=''),
            dict(id=4, label='Pascal', language=Submission.LANGUAGE_PASCAL, version=''),
            dict(id=5, label='Java', language=Submission.LANGUAGE_JAVA, version=''),
            dict(id=6, label='C#', language=Submission.LANGUAGE_CSHARP, version=''),
        ]

    # def get_all_contest_numbers(self):
    #     soup = request_dom(urljoin(self.homepage, '/JudgeOnline/contest.php'), self.charset)
    #     results = soup.select('table')[1].select
    #     nums = []
    #     for a in results:
    #         matches = re.findall(r'/onlinejudge/showContestProblems\.do\?contestId=(\d+)', a.attrs.get('href'))
    #         if matches:
    #             nums.append(matches[0])
    #     return sorted(nums)

    def get_all_problem_numbers(self):
        nums = set()
        base_url = urljoin(self.homepage, '/listproblem.php')
        content = request_text(base_url, self.charset)

        def get_page(link):
            # print(link)
            html = request_text(urljoin(base_url, link), self.charset)
            nums.update(re.findall(r'p\(\d+,(\d+),', html))

        from threading import Thread
        threads = []
        for link in set(re.findall(r'listproblem.php\?vol=\d+', content)):
            threads.append(Thread(target=get_page, args=[link]))
            get_page(link)

        [t.start() for t in threads]
        [t.join() for t in threads]

        return sorted(nums)

    def get_problem_url(self, problem_id, contest_id=None):
        return urljoin(self.homepage,
                       '/contest/contest_showproblem.php?pid={}&cid={}'.format(problem_id, contest_id)) if contest_id \
            else urljoin(self.homepage, '/showproblem.php?pid={}'.format(problem_id))

    def parse_problem(self, body, current_url=''):
        # 构造空白问题对象
        problem = Problem()
        problem.input_samples = []
        problem.output_samples = []
        problem.extra_info = dict()
        # 开始处理
        dom = BeautifulSoup(body, 'lxml')

        # 标题行
        problem.title = dom.select_one('h1').text
        # 附加信息行
        info = dom.select_one('h1').next_sibling()[0].text
        problem.time_limit = int(re.search(r'(\d+) MS', info).groups()[0])
        problem.memory_limit = int(re.search(r'(\d+) K', info).groups()[0])
        problem.is_special_judge = 'Special Judge' in info
        problem.extra_info = {}
        # desciption
        for title, field, tp in [
            ('Problem Description', 'description', 'text'),
            ('Input', 'input_specification', 'text'),
            ('Output', 'output_specification', 'text'),
            ('Sample Input', 'input_samples', 'data'),
            ('Sample Output', 'output_samples', 'data'),
            ('Author', 'author', 'info'),
            ('Source', 'source', 'info'),
            ('Recommend', 'recommend', 'info'),
        ]:
            node = dom.find(text=title)
            if not node:
                continue
            for el in node.parent.next_siblings:
                if el.name == 'div' and 'panel_content' in el['class']:
                    if tp == 'text':
                        # MathJax 限定符归一化为 $$$
                        setattr(problem, field,
                                re.sub(r'(?<!\\)\$', '$$$', self.sanitize_html(el.decode_contents(), current_url)))
                    elif tp == 'data':
                        hint = el.find(text='Hint')
                        if hint:
                            # 好恶心啊，不知道1023是不是特例
                            parent = hint.parent.parent.parent
                            # while parent.parent != el:
                            #     parent = parent.parent
                            hint.parent.decompose()
                            problem.extra_description = self.sanitize_html(parent.decode_contents(), current_url)
                            parent.decompose()
                        setattr(problem, field, [el.text.replace('\r\n', '\n').rstrip(' \n').strip('\n')])
                    elif tp == 'info':
                        data = self.sanitize_html(el.decode_contents(), current_url)
                        if data:
                            problem.extra_info[field] = data
                    break
        problem.extra_info = json.dumps(problem.extra_info)

        # problem.print()
        return problem

    def get_user_context_by_user_and_password(self, username, password):
        context = UserContext()
        resp = context.session.post(
            url=urljoin(self.homepage, '/userloginex.php?action=login'),
            data=dict(username=username, userpass=password, login='Sign In'),
        )
        if resp.status_code >= 400:
            return None
        # context.save()
        return context

    def check_context_validity(self, context):
        resp = context.session.get(self.homepage)
        content = resp.content.decode(self.charset)
        return 'alt="Sign Out"' in content

    def _get_current_handle(self, context):
        resp = context.session.get(self.homepage)
        content = resp.content.decode(self.charset)
        matches = re.search(r'/userstatus\.php\?user=([^\"]+)" style', content)
        if matches:
            return matches.groups()[0]

    def get_user_solved_problem_list(self, context):
        """ 获取用户已通过题目列表 """
        content = request_text(urljoin(
            self.homepage,
            '/userstatus.php?user={}'.format(self._get_current_handle(context))
        ), self.charset, context)
        return re.findall(r'p\((\d+),[1-9]\d*,\d+\)', content)

    def get_user_failed_problem_list(self, context):
        """ 获取用户未通过题目列表 """
        content = request_text(urljoin(
            self.homepage,
            '/userstatus.php?user={}'.format(self._get_current_handle(context))
        ), self.charset, context)
        return re.findall(r'p\((\d+),0,\d+\)', content)

    def _parse_submission_row(self, context, row):
        status_map = {
            'Accepted': Submission.RESULT_ACCEPTED,
            'Wrong Answer': Submission.RESULT_WRONG_ANSWER,
            'Presentation Error': Submission.RESULT_PRESENTATION_ERROR,
            'Compilation Error': Submission.RESULT_COMPILATION_ERROR,
            'Runtime Error.+': Submission.RESULT_RUNTIME_ERROR,
            'Time Limit Exceeded': Submission.RESULT_TIME_LIMIT_EXCEED,
            'Memory Limit Exceeded': Submission.RESULT_MEMORY_LIMIT_EXCEED,
            'Output Limit Exceed': Submission.RESULT_OUTPUT_LIMIT_EXCEED,
        }
        submission_id = row.select_one('td').text
        problem_id = row.select('td')[3].text

        # print(row.select_one('.runJudgeStatus').text.strip())
        submission = Submission(
            id=submission_id,
            submit_time=row.select('td')[1].text,
            problem_id=problem_id,
            language_id=self.get_language_id_by('label', row.select('td')[7].text.strip()),
        )
        for key, val in status_map.items():
            if re.match(key, row.select('td')[2].text.strip()):
                submission.result = val
                break
        if re.match(r'(\d+)MS', row.select('td')[4].text):
            submission.run_time = int(re.match(r'(\d+)MS', row.select('td')[4].text).groups()[0])
        if re.match(r'(\d+)K', row.select('td')[5].text):
            submission.run_memory = int(re.match(r'(\d+)K', row.select('td')[5].text).groups()[0])
        # 获取代码
        dom = request_dom(urljoin(
            self.homepage,
            '/viewcode.php?rid={}'.format(submission_id)
        ), self.charset, context)
        import html
        submission.code = html.unescape(dom.select_one('#usercode').decode_contents().replace('\r\n', '\n'))
        return submission

    def _query_submission(self, context, last_id='', handle=''):
        url = urljoin(
            self.homepage,
            '/status.php?user={handle}&first={last_id}&pid=0&lang=0&status=0#status'.format(
                handle=handle, last_id=last_id)
        )
        resp = context.session.get(url=url)
        content = resp.content.decode(self.charset)
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('table.table_text tr')[1:]
        # next page link
        matches = re.search(r'/status\.php\?first=(\d+)&user={}'.format(handle), content)
        first = matches.groups()[0] if matches else None
        return rows, first

    def get_user_submission_list(self, context, excludes=()):
        """ 获取用户的提交列表
        TODO: 这个方法太重了，一跑起来没完没了，后面考虑一下优化的问题，将抓取任务切碎
        """
        handle = self._get_current_handle(context)
        results = []
        next_id = '0'
        # TODO: excludes 尚未实现
        while next_id:
            rows, next_id = self._query_submission(context, last_id=next_id, handle=handle)
            for row in rows:
                submission = self._parse_submission_row(context, row)
                # print(submission.id, submission.submit_time)
                results.append(submission)
                # print(submission.__dict__)
            from sys import stdout
            stdout.flush()
            # break
        return results

    def submit_problem(self, context, problem_id, language, code, contest_id=None):
        # 提交代码
        resp = context.session.post(
            url=urljoin(self.homepage, '/submit.php?action=submit'),
            data=dict(
                check=0,
                problemid=problem_id,
                language=language,
                usercode=code,
            ),
        )
        # 获取最近一次提交的编号
        handle = self._get_current_handle(context)
        rows, _ = self._query_submission(context, last_id='0', handle=handle)
        submission = self._parse_submission_row(context, rows[0])
        submission_id = submission.id
        # 获取结果
        retry = 10
        while True:
            rows, next_id = self._query_submission(context, submission_id)
            # print(rows, next_id)
            # print(rows[0].select_one('.judgeReplyOther').text.strip())
            submission = self._parse_submission_row(context, rows[0])
            retry -= 1
            if submission.result or not retry:
                break
            from time import sleep
            sleep(11 - retry)
        return submission
