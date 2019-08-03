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


class OJAdapterBZOJ(OJAdapterBase):
    """
    BZOJ 要校验 UserAgent，直接抓会 404。
    BZOJ 的换行排版很混乱，有些用 div，有些用 br，而且全部硬换行，所以只能将就了。
    """
    # TODO: 有一类 pdf 内链类型的题目有必要将目标保存到本站，例如 5509

    name = '大视野在线评测'
    code = 'BZOJ'
    charset = 'utf8'
    homepage = r'https://lydsy.com'
    platform_username = 'actips'
    platform_password = 'Actips@2019'
    platform_email = 'admin@actips.org'

    def get_supported_languages(self):
        return [
            dict(id=0, label='C', language=Submission.LANGUAGE_C, version='gcc 4.4.5'),
            dict(id=1, label='C++', language=Submission.LANGUAGE_CPP, version='glibc 2.3.6'),
            dict(id=2, label='Pascal', language=Submission.LANGUAGE_PASCAL, version='Free Pascal 2.4.0-2'),
            dict(id=3, label='Java', language=Submission.LANGUAGE_JAVA, version='Java 1.6.0_162'),
            dict(id=4, label='Ruby', language=Submission.LANGUAGE_RUBY, version=''),
            dict(id=5, label='Bash', language=Submission.LANGUAGE_BASH, version=''),
            dict(id=6, label='Python', language=Submission.LANGUAGE_PYTHON2, version='PHP 7.2.13'),
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
        from threading import Thread
        # 获取种子页
        base_url = urljoin(self.homepage, '/JudgeOnline/problemset.php')
        soup = request_dom(base_url, self.charset)
        nums = set()

        def parse_numbers_from_url(url):
            sp = request_dom(url, self.charset)
            for tr in sp.select('table#problemset tbody tr'):
                if len(tr) != 6:
                    continue
                num = int(tr.select('td')[1].text)
                nums.add(num)

        t = Thread(target=parse_numbers_from_url, args=[base_url])
        t.start()
        threads = [t]
        for a in soup.select('h3 a'):
            href = a.attrs.get('href')
            if href and href.startswith('problemset.php?page='):
                t = Thread(target=parse_numbers_from_url, args=[urljoin(base_url, href)])
                t.start()
                threads.append(t)
        for t in threads:
            t.join()
        # print(nums)
        return sorted(nums)

    def get_problem_url(self, problem_id, contest_id=None):
        return urljoin(self.homepage, '/JudgeOnline/problem.php?id={}'.format(problem_id))

    def parse_problem(self, body, current_url=''):
        # 构造空白问题对象
        problem = Problem()
        problem.input_samples = []
        problem.output_samples = []
        problem.extra_info = dict()
        # 开始处理
        dom = BeautifulSoup(body, 'lxml')
        section = ''
        cache = ''

        def commit_section():
            nonlocal cache
            """ 保存一个信息节 """
            if section == 'Description':
                cache = re.sub(r'<br\s*/?>', '', cache)
                problem.description = self.sanitize_html(cache, current_url)
            elif section == 'Input':
                cache = re.sub(r'<br\s*/?>', '', cache)
                problem.input_specification = self.sanitize_html(cache, current_url)
            elif section == 'Output':
                cache = re.sub(r'<br\s*/?>', '', cache)
                problem.output_specification = self.sanitize_html(cache, current_url)
            elif section == 'HINT':
                cache = re.sub(r'<br\s*/?>', '', cache)
                problem.extra_description = self.sanitize_html(cache, current_url)
            elif section == 'Source':
                if not cache.strip():
                    return
                problem.extra_info['source'] = self.sanitize_html(cache, current_url).strip()
            elif section == 'Sample Input':
                data = html2text(cache).strip('\n')
                data = '\n'.join([re.sub(r'\s\s$', '', line) for line in data.split('\n')])
                problem.input_samples = [data]
            elif section == 'Sample Output':
                data = html2text(cache).strip('\n')
                data = '\n'.join([re.sub(r'\s\s$', '', line) for line in data.split('\n')])
                problem.output_samples = [data]

        for block in dom.select('body > *'):
            block_content = block.decode_contents()
            # 跳过标题行
            if 'image/logo.png' in block_content:
                continue
            elif block.name == 'title':
                matches = re.match(r'Problem \d+\.\s+--\s+(.+)', block_content)
                if matches:
                    problem.title = matches.groups()[0]
            elif block.name == 'center' and 'Time Limit:' in block_content:
                matches = re.search(r'Time Limit:\s+</span>\s*(\d+(?:\.\d+)?)\s+Sec', block_content)
                if matches:
                    problem.time_limit = int(float(matches.groups()[0]) * 1000)
                matches = re.search(r'Memory Limit:\s+</span>\s*(\d+(?:\.\d+)?)\s+MB', block_content)
                if matches:
                    problem.memory_limit = int(matches.groups()[0]) * 1024
            elif block.name == 'h2':
                if block_content in {'Description', 'Input', 'Output',
                                     'Sample Input', 'Sample Output', 'HINT', 'Source'}:
                    commit_section()
                    section = block_content
                    cache = ''
            elif block.name == 'div':
                cache += block_content

        # problem.print()
        return problem

    def get_user_context_by_user_and_password(self, username, password):
        context = UserContext()
        resp = context.session.post(
            url=urljoin(self.homepage, '/JudgeOnline/login.php'),
            data=dict(user_id=username, password=password, submit='Submit'),
        )
        if resp.status_code >= 400:
            return None
        # context.save()
        return context

    def check_context_validity(self, context):
        resp = context.session.get(urljoin(self.homepage, '/JudgeOnline/'))
        content = resp.content.decode(self.charset)
        return '<a href=logout.php' in content

    def get_user_solved_problem_list(self, context):
        """ 获取用户已通过题目列表 """
        dom = request_dom(urljoin(
            self.homepage,
            '/JudgeOnline/userinfo.php?user={}'.format(self._get_current_handle(context))
        ), self.charset, context)
        txt = dom.select_one('td[rowspan=14]').decode_contents()
        return re.findall(r'p\((\d+)\)', txt)

    # def get_user_failed_problem_list(self, context):
    #     """ 获取用户未通过题目列表 """
    #     # 可以后面翻一下提交记录
    #     # ZOJ 并没有列出这个信息
    #     return []

    def _parse_submission_row(self, context, row):
        status_map = {
            'Accepted': Submission.RESULT_ACCEPTED,
            'Presentation_Error': Submission.RESULT_PRESENTATION_ERROR,
            'Wrong_Answer': Submission.RESULT_WRONG_ANSWER,
            'Time_Limit_Exceeded': Submission.RESULT_TIME_LIMIT_EXCEED,
            'Memory_Limit_Exceeded': Submission.RESULT_MEMORY_LIMIT_EXCEED,
            'Compile_Error': Submission.RESULT_COMPILATION_ERROR,
            'Output_Limit_Exceed': Submission.RESULT_OUTPUT_LIMIT_EXCEED,
            'Runtime_Error': Submission.RESULT_RUNTIME_ERROR,
        }
        submission_id = row.select_one('td').text
        problem_id = row.select('td')[2].text
        td_lang = row.select('td')[6]
        is_self = td_lang.select_one('a')
        # print(row.select_one('.runJudgeStatus').text.strip())
        submission = Submission(
            id=submission_id,
            submit_time=row.select('td')[8].text,
            result=status_map.get(row.select('td')[3].text.strip()) or '',
            problem_id=problem_id,
            language_id=self.get_language_id_by('label', is_self.text if is_self else td_lang.text),
        )
        if re.match(r'(\d+) ms', row.select('td')[5].text):
            submission.run_time = int(re.match(r'(\d+) ms', row.select('td')[5].text).groups()[0])
        if re.match(r'(\d+) kb', row.select('td')[4].text):
            submission.run_memory = int(re.match(r'(\d+) kb', row.select('td')[4].text).groups()[0])
        if is_self:
            dom = request_dom(urljoin(
                self.homepage,
                '/JudgeOnline/submitpage.php?id={}&sid={}'.format(problem_id, submission_id)
            ), self.charset, context)
            submission.code = dom.select_one('textarea').decode_contents()
        return submission

    def _get_current_handle(self, context):
        resp = context.session.get(urljoin(self.homepage, '/JudgeOnline/'))
        content = resp.content.decode(self.charset)
        matches = re.search(r'userinfo\.php\?user=([^\']+)', content)
        if matches:
            return matches.groups()[0]

    def _query_submission(self, context, last_id=''):
        self._get_current_handle(context)
        resp = context.session.get(
            url=urljoin(
                self.homepage,
                '/JudgeOnline/status.php?user_id={handle}&top={last_id}'.format(
                    handle=self._get_current_handle(context), last_id=last_id)
            )
        )
        content = resp.content.decode(self.charset)
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('table[align=center] tr')[1:]
        # next page link
        matches = re.search(r'top=(\d+)&prevtop=(\d+)>Next Page</a', content)
        if not matches:
            return None
        top, prev_top = matches.groups()
        if rows[-1].select_one('td').text == top:
            # 如果下一页的首个 ID 等于当前页最后一个ID说明已经没有下一页了
            top = None
        return rows, top

    def get_user_submission_list(self, context, excludes=()):
        """ 获取用户的提交列表
        TODO: 这个方法太重了，一跑起来没完没了，后面考虑一下优化的问题，将抓取任务切碎
        """
        results = []
        next_id = -1
        # TODO: excludes 尚未实现
        while next_id:
            rows, next_id = self._query_submission(context, last_id=next_id)
            for row in rows[1:]:
                submission = self._parse_submission_row(context, row)
                # print(submission.id, submission.submit_time)
                results.append(submission)
                # print(submission.__dict__)
        return results

    def submit_problem(self, context, problem_id, language, code, contest_id=None):
        # 实际提交的 problemID 和题目的 problem_id 不一致，需要先抓过来转换一下
        # 映射 language_id
        # 提交代码
        resp = context.session.post(
            url=urljoin(self.homepage, '/JudgeOnline/submit.php'),
            data=dict(
                id=problem_id,
                language=language,
                source=code,
            ),
        )
        soup = BeautifulSoup(resp.content.decode(self.charset), 'lxml')
        submission_id = soup.select_one('tr.evenrow td').text
        # print(submission_id)
        # print('>>> submission_id: {}'.format(submission_id))
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
