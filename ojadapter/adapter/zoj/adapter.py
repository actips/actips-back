import re

import requests
from bs4 import BeautifulSoup
from html2text import html2text

from ojadapter.entity.Problem import Problem
from ojadapter.entity.UserContext import UserContext
from ...utils import request_dom, request_text
from ..OJAdapterBase import OJAdapterBase
from urllib.parse import urljoin


class OJAdapterZOJ(OJAdapterBase):
    code = 'ZOJ'
    homepage = r'http://acm.zju.edu.cn'

    platform_username = 'actips'
    platform_password = 'Actips@2019'

    # def get_supported_languages(self):
    #     return 1

    def get_all_contest_numbers(self):
        soup = request_dom(urljoin(self.homepage, '/onlinejudge/showContests.do'), self.charset)
        results = soup.select('td.contestName > a')
        nums = []
        for a in results:
            matches = re.findall(r'/onlinejudge/showContestProblems\.do\?contestId=(\d+)', a.attrs.get('href'))
            if matches:
                nums.append(matches[0])
        return sorted(nums)

    def get_all_problem_numbers(self):
        # 获取种子页
        soup = request_dom(urljoin(self.homepage, '/onlinejudge/showProblemsets.do'), self.charset)
        results = soup.select('#content_body form > a')
        threads = []
        nums = []

        def parse_numbers_from_url(url):
            sp = request_dom(url, self.charset)
            for a in sp.select('.problemId a'):
                # print(a)
                matches = re.findall(r'/onlinejudge/showProblem\.do\?problemCode=(\d+)', a.attrs.get('href'))
                if matches:
                    nums.append(matches[0])

        for a in results:
            href = a.attrs.get('href')
            if href and href.startswith('/onlinejudge/showProblems.do'):
                from threading import Thread
                t = Thread(
                    target=parse_numbers_from_url,
                    args=[urljoin(self.homepage, href)]
                )
                t.start()
                threads.append(t)
        for t in threads:
            t.join()
        # print(nums)
        return sorted(nums)

    def get_problem_url(self, problem_id, contest_id=None):
        if contest_id:
            return urljoin(self.homepage, '/onlinejudge/showContestProblem.do?problemId={}'.format(problem_id))
        else:
            return urljoin(self.homepage, '/onlinejudge/showProblem.do?problemCode={}'.format(problem_id))

    def parse_problem(self, body):
        problem = Problem()
        dom = BeautifulSoup(body, 'lxml')
        # 解析标题
        problem.title = dom.select('.bigProblemTitle')[0].text
        # 解析时间限制、Special Judge
        row_limit = dom.select('#content_body > center')[1].text
        problem.time_limit = int(re.findall(r'Time Limit:\s+(\d+)\s+Seconds?', row_limit)[0])
        problem.memory_limit = int(re.findall(r'Memory Limit:\s+(\d+)\s+KB', row_limit)[0])
        problem.is_special_judge = 'Special Judge' in row_limit
        # 解析正文内容
        content = dom.select('#content_body')[0].encode_contents().decode(self.charset)
        # print(content)
        parser = re.compile(
            r'<hr/>(?:.|\n)+<hr/>((?:.|\n)+)'  # ?P<description>
            r'(?:(?:<p><b>|<h4>)Input(?:</h4>|</b>[\s\n]*</p>))((?:.|\n)+)'  # ?P<input_specification>
            r'(?:(?:<p><b>|<h4>)Output(?:</h4>|</b>[\s\n]*</p>))((?:.|\n)+)'  # ?P<output_specification>
            r'(?:<h4>Sample Input</h4>[\s\n]*<pre>((?:.|\n)+)</pre>[\s\n]*)'  # ?P<input_sample>
            r'(?:<h4>Sample Output</h4>[\s\n]*<pre>((?:.|\n)+)</pre>[\s\n]*)'  # ?P<input_sample>
            r'((?:.|\n)*)?<hr/>[\s\n]*'  # ?P<extra_description>
            r'(?:Author:\s+<strong>(.+)</strong><br/>[\s\n]+)?'  # ?P<author>
            r'(?:Source:\s+<strong>(.+)</strong><br/>[\s\n]+)?'  # ?P<source>
            r'<center>'
            , re.MULTILINE
        )
        match = parser.search(content)
        (description, input_specification, output_specification,
         input_samples, output_samples, extra_description, author, source) = match.groups()
        problem.description = html2text(description or '').strip()
        problem.extra_description = html2text(extra_description or '').strip()
        problem.input_specification = html2text(input_specification or '').strip()
        problem.output_specification = html2text(output_specification or '').strip()
        problem.input_samples = [input_samples.strip().replace('\r\n', '\n').replace('\r', '\n')]
        problem.output_samples = [output_samples.strip().replace('\r\n', '\n').replace('\r', '\n')]
        problem.author = (author or '').strip()
        problem.source = (source or '').strip()
        return problem

    def get_user_context_by_user_and_password(self, username, password):
        context = UserContext()
        resp = context.session.post(
            url=urljoin(self.homepage, 'onlinejudge/login.do'),
            data=dict(handle=username, password=password, rememberMe='on'),
        )
        if resp.status_code >= 400:
            return None
        # context.save()
        return context

    def check_context_validity(self, context):
        resp = context.session.get(urljoin(self.homepage, 'onlinejudge'))
        content = resp.content.decode(self.charset)
        groups = re.findall(r'showUserStatus\.do\?userId=(\d+)', content)
        return bool(groups)

    def get_user_solved_problem_list(self, context):
        """ 获取用户已通过题目列表 """
        # 获取用户 id
        resp = context.session.get(urljoin(self.homepage, 'onlinejudge'))
        content = resp.content.decode(self.charset)
        # print(content)
        groups = re.findall(r'showUserStatus\.do\?userId=(\d+)', content)
        # print(groups)
        user_id = groups[0]
        # 获取状态页面
        resp = context.session.get(urljoin(
            self.homepage, 'onlinejudge/showUserStatus.do?userId={}'.format(user_id)
        ))
        problem_ids = re.findall(r'href="/onlinejudge/showProblem\.do\?problemCode=(\d+)"',
                                 resp.content.decode(self.charset))
        return problem_ids

    def get_user_failed_problem_list(self, context):
        """ 获取用户未通过题目列表 """
        # 可以后面翻一下提交记录
        # ZOJ 并没有列出这个信息
        return []

    def get_user_submission_list(self, context, excludes=()):
        """ 获取用户的提交列表 """
        from ojadapter.entity.Submission import Submission
        handle = context.session.cookies['oj_handle']
        results = []

        status_map = {
            'Accepted': Submission.RESULT_ACCEPTED,
            'Presentation Error': Submission.RESULT_PRESENTATION_ERROR,
            'Wrong Answer': Submission.RESULT_WRONG_ANSWER,
            'Time Limit Exceeded': Submission.RESULT_TIME_LIMIT_EXCEED,
            'Memory Limit Exceeded': Submission.RESULT_MEMORY_LIMIT_EXCEED,
            'Segmentation Fault': Submission.RESULT_SEGMENT_FAULT,
            'Non-zero Exit Code': Submission.RESULT_NON_ZERO_EXIT_CODE,
            'Floating Point Error': Submission.RESULT_FLOAT_POINT_ERROR,
            'Compilation Error': Submission.RESULT_COMPILATION_ERROR,
            'Output Limit Exceed': Submission.RESULT_OUTPUT_LIMIT_EXCEED,
            'Runtime Error': Submission.RESULT_RUNTIME_ERROR,
        }

        language_map = {
            'C': Submission.LANGUAGE_C,
            'C++': Submission.LANGUAGE_GPP,
            'FPC': Submission.LANGUAGE_FPC,
            'Java': Submission.LANGUAGE_JAVA,
            'Python': Submission.LANGUAGE_PYTHON2,
            'Perl': Submission.LANGUAGE_PERL,
            'Scheme': Submission.LANGUAGE_SCHEME,
            'PHP': Submission.LANGUAGE_PHP,
            'C++11': Submission.LANGUAGE_CPP11,
        }

        def get_list(last=-1):
            resp = context.session.get(
                url=urljoin(
                    self.homepage,
                    '/onlinejudge/showRuns.do'
                    '?contestId=1&search=true'
                    '&firstId=-1&lastId={}&problemCode='
                    '&handle={}&idStart=&idEnd='.format(
                        last, context.session.cookies['oj_handle']
                    )
                )
            )
            content = resp.content.decode(self.charset)
            # print(content)
            soup = BeautifulSoup(content, 'lxml')
            rows = soup.select('table.list tr')
            for row in rows[1:]:
                submission_id = row.select_one('.runId').text
                if submission_id in excludes:
                    continue
                # print(row.select_one('.runJudgeStatus').text.strip())
                submission = Submission(
                    id=submission_id,
                    submit_time=row.select_one('.runSubmitTime').text,
                    result=status_map.get(row.select_one('.runJudgeStatus').text.strip()),
                    problem_id=row.select_one('.runProblemId').text,
                    language=language_map.get(row.select_one('.runLanguage').text),
                    run_time=int(row.select_one('.runTime').text or -1),
                    run_memory=int(row.select_one('.runMemory').text or -1),
                )
                # print(row)
                code = context.session \
                           .get(urljoin(self.homepage, row.select_one('.runLanguage a').attrs.get('href'))) \
                           .content.decode(self.charset)
                submission.code = code
                results.append(submission)
                # print(submission.__dict__)
            # next page link
            groups = re.findall(r'JavaScript: goNext\((\d+)\);', content)
            if groups:
                get_list(groups[0])

        get_list()
        return results
