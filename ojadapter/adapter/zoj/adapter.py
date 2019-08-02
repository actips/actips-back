import json
import re

import requests
from bs4 import BeautifulSoup
from html2text import html2text

from ojadapter.entity.Problem import Problem
from ojadapter.entity.UserContext import UserContext
from ojadapter.entity.Submission import Submission
from ...utils import request_dom, request_text
from ..OJAdapterBase import OJAdapterBase
from urllib.parse import urljoin


class OJAdapterZOJ(OJAdapterBase):
    name = '浙江大学 Online Judge'
    code = 'ZOJ'
    charset = 'utf8'
    homepage = r'http://acm.zju.edu.cn'

    platform_username = 'actips'
    platform_password = 'Actips@2019'
    platform_email = 'admin@actips.org'

    def get_supported_languages(self):
        return [
            dict(id=1, label='C', language=Submission.LANGUAGE_C, version='gcc 4.7.2'),
            dict(id=2, label='C++', language=Submission.LANGUAGE_CPP, version='g++ 4.7.2'),
            dict(id=3, label='FPC', language=Submission.LANGUAGE_PASCAL, version='fpc 2.6.0'),
            dict(id=4, label='Java', language=Submission.LANGUAGE_JAVA, version='java 1.7.0'),
            dict(id=5, label='Python', language=Submission.LANGUAGE_PYTHON2, version='Python 2.7.3'),
            dict(id=6, label='Perl', language=Submission.LANGUAGE_PERL, version='Perl 5.14.2'),
            dict(id=7, label='Scheme', language=Submission.LANGUAGE_SCHEME, version='Guile 1.8.8'),
            dict(id=8, label='PHP', language=Submission.LANGUAGE_PHP, version='PHP 5.4.4'),
            dict(id=9, label='C++11', language=Submission.LANGUAGE_CPP, version='g++ 4.7.2'),
        ]

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

    def parse_problem(self, body, current_url=''):
        # 构造空白问题对象
        problem = Problem()
        problem.input_samples = ''
        problem.output_samples = ''
        problem.extra_info = dict()
        # 开始处理
        dom = BeautifulSoup(body, 'lxml')
        # 抓取的题目编号
        titles = dom.select_one('#content_title').text.split(' - ')
        pid = int(titles[1 if len(titles) == 2 else 0])
        # 解析标题
        problem.title = dom.select('.bigProblemTitle')[0].text.strip()
        # 解析时间限制、Special Judge
        row_limit = dom.select('#content_body > center')[1].text
        problem.time_limit = int(re.findall(r'Time Limit:\s+(\d+)\s+Seconds?', row_limit)[0]) * 1000  # 转化为毫秒
        problem.memory_limit = int(re.findall(r'Memory Limit:\s+(\d+)\s+KB', row_limit)[0])
        problem.is_special_judge = 'Special Judge' in row_limit
        # 解析正文内容
        # content = dom.select('#content_body')[0].encode_contents().decode(self.charset)
        # print(content)
        parser = re.compile(r'<div id="content_body">((?:.|\n)+)'
                            r'<center>[\s\n]+<a href="/onlinejudge/(?:contestSubmit|submit).do', re.MULTILINE)
        match = parser.search(body)
        content = match[1]

        # 补刀，有些很特别的恶心情况，例如 2813，它的数据是放在一个表格里面的，这种情况要特殊处理：
        soup = BeautifulSoup(content, 'lxml')
        # print(contentSoup)
        for table in soup.select('table'):
            thead_tds = table.select('thead td')
            if len(thead_tds) == 2 and thead_tds[0].text == 'Example input:' and \
                    table.select('thead td')[1].text == 'Example output:':
                problem.input_samples = \
                    '\n'.join([l.strip() for l in table.select('tbody td')[0].text.split('\n')]).strip()
                problem.output_samples = \
                    '\n'.join([l.strip() for l in table.select('tbody td')[1].text.split('\n')]).strip()
                pattern = re.compile(r'<table(?:.|\n)*<thead(?:.|\n)*Example input(?:.|\n)*</table>', re.MULTILINE)
                content = pattern.sub('', content)

        # parser = re.compile(
        #     r'<hr/>(?:.|\n)+<hr/>((?:.|\n)+)'  # ?P<description>
        #     r'(?:(?:<p><b>|<h4>)Input(?:</h4>|</b>[\s\n]*</p>))((?:.|\n)+)'  # ?P<input_specification>
        #     r'(?:(?:<p><b>|<h4>)Output(?:</h4>|</b>[\s\n]*</p>))((?:.|\n)+)'  # ?P<output_specification>
        #     r'(?:<h4>Sample Input</h4>[\s\n]*<pre>((?:.|\n)+)</pre>[\s\n]*)'  # ?P<input_sample>
        #     r'(?:<h4>Sample Output</h4>[\s\n]*<pre>((?:.|\n)+)</pre>[\s\n]*)'  # ?P<input_sample>
        #     r'((?:.|\n)*)?<hr/>[\s\n]*'  # ?P<extra_description>
        #     r'(?:Author:\s+<strong>(.+)</strong><br/>[\s\n]+)?'  # ?P<author>
        #     r'(?:Source:\s+<strong>(.+)</strong><br/>[\s\n]+)?'  # ?P<source>
        #     r'(?:Contest:\s+<strong>(.+)</strong><br/>[\s\n]+)?'  # ?P<contest>
        #     r'(?:.|\n)*<center>'
        #     , re.MULTILINE
        # )
        # match = parser.search(content)
        # if match:
        #     (description, input_specification, output_specification, input_samples, output_samples,
        #      extra_description, author, source, contest) = match.groups()
        #     problem.description = html2text(description or '').strip()
        #     problem.extra_description = html2text(extra_description or '').strip()
        #     problem.input_specification = html2text(input_specification or '').strip()
        #     problem.output_specification = html2text(output_specification or '').strip()
        #     problem.input_samples = [input_samples.strip().replace('\r\n', '\n').replace('\r', '\n')]
        #     problem.output_samples = [output_samples.strip().replace('\r\n', '\n').replace('\r', '\n')]
        #     problem.extra_info = json.dumps(dict(
        #         author=(author or '').strip(),
        #         source=(source or '').strip(),
        #         contest=(contest or '').strip()
        #     ))
        #     return problem

        # 直接转化为 Markdown 再处理
        _content = html2text(content.replace('\r\n', '\n'), bodywidth=0)
        # print(_content)
        parts = [x.strip() for x in _content.split('* * *')]

        stage = 0

        # 特殊格式补刀，例如 1067-1075
        example_flag = False

        for line in parts[2].split('\n'):

            # 特殊格式补刀，例如 1067-1075
            if re.match(r'^[^\w]*(?:ex|s)ample[^\w]*$', line.lower()):
                example_flag = True
                continue

            # 分块
            if re.match(r'^[^\w]*input(?: format)?[^\w]*$', line.lower()):
                stage = 3 if example_flag else 1  # 主要为了照顾 1067-1075 这种格式
                continue
            elif re.match(r'^[^\w]*output(?: format)?[^\w]*$', line.lower()):
                stage = 4 if example_flag else 2  # 主要为了照顾 1067-1075 这种格式
                continue
            elif re.match(r'^[^\w]*(?:ex|s)ample\s*input[^\w]*$', line.lower()):
                stage = 3
                continue
            elif re.match(r'^[^\w]*(?:ex|s)ample\s*output[^\w]*$', line.lower()) \
                    or re.match(r'^[^\w]*output for (?:the )?sample input[^\w]*$', line.lower()):
                stage = 4
                continue

            # 特殊格式补刀，例如2813
            if line.startswith('**Input:**'):
                stage = 1
                line = line.replace('**Input:**', '')
            if line.startswith('**Output:**'):
                stage = 2
                line = line.replace('**Output:**', '')

            # 1134-1141 特殊处理（input/output实际上是数据，没有specifications）
            if 1134 <= pid <= 1141:
                stage = 4 if stage == 2 else 3 if stage == 1 else stage

            # extra_description after sample data
            if 3 <= stage <= 4 and line.strip() \
                    and line.startswith('#') or re.match(r'^\*.+\*$', line):
                stage = 5

            # 导入
            if stage == 0:
                problem.description += line + '\n'
            elif stage == 1:
                problem.input_specification += line + '\n'
            elif stage == 2:
                problem.output_specification += line + '\n'
            elif stage == 3:
                problem.input_samples += (line[4:] if line.startswith('    ') else line) + '\n'
            elif stage == 4:
                problem.output_samples += (line[4:] if line.startswith('    ') else line) + '\n'
            else:
                problem.extra_description += line + '\n'

        for line in parts[3].split('\n'):
            if ':' in line:
                pos = line.find(':')
                key = line[:pos].strip().lower()
                val = line[pos + 1:].strip('* ')
                problem.extra_info[key] = val

        problem.description = self.sanitize_markdown(problem.description.strip(), current_url)
        problem.input_specification = self.sanitize_markdown(problem.input_specification.strip(), current_url)
        problem.output_specification = self.sanitize_markdown(problem.output_specification.strip(), current_url)
        problem.input_samples = [problem.input_samples.strip()]
        problem.output_samples = [problem.output_samples.strip()]
        problem.extra_description = self.sanitize_markdown(problem.extra_description.strip(), current_url)
        problem.extra_info = json.dumps(problem.extra_info)

        # problem.print()
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

    # def get_user_failed_problem_list(self, context):
    #     """ 获取用户未通过题目列表 """
    #     # 可以后面翻一下提交记录
    #     # ZOJ 并没有列出这个信息
    #     return []

    def _parse_submission_row(self, context, row):
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
            'Output Limit Exceeded': Submission.RESULT_OUTPUT_LIMIT_EXCEED,
            'Runtime Error': Submission.RESULT_RUNTIME_ERROR,
        }
        language_id = self.get_language_id_by('label', row.select_one('.runLanguage').text)
        submission_id = row.select_one('.runId').text
        # print(row.select_one('.runJudgeStatus').text.strip())
        # print(row.select_one('.runLanguage').text, language_id)
        submission = Submission(
            id=submission_id,
            submit_time=row.select_one('.runSubmitTime').text,
            result=status_map.get(row.select_one('.runJudgeStatus').text.strip()) or '',
            problem_id=row.select_one('.runProblemId').text,
            language_id=language_id,
            run_time=int(row.select_one('.runTime').text or -1),
            run_memory=int(row.select_one('.runMemory').text or -1),
        )
        # print(row)
        code = context.session \
            .get(urljoin(self.homepage, row.select_one('.runLanguage a').attrs.get('href'))) \
            .content.decode(self.charset)
        submission.code = code
        return submission

    def _query_submission(self, context, handle=None, first_id=-1, last_id=-1, id_start='', id_end=''):
        handle = handle or context.session.cookies['oj_handle']
        resp = context.session.get(
            url=urljoin(
                self.homepage,
                '/onlinejudge/showRuns.do'
                '?contestId=1&search=true'
                '&firstId={}&lastId={}&problemCode='
                '&handle={}&idStart={}&idEnd={}'.format(
                    first_id, last_id, handle, id_start, id_end)
            )
        )
        content = resp.content.decode(self.charset)
        soup = BeautifulSoup(content, 'lxml')
        rows = soup.select('table.list tr')[1:]
        # next page link
        groups = re.findall(r'JavaScript: goNext\((\d+)\);', content)
        next_id = groups[0] if groups else None
        return rows, next_id

    # def get_user_submission(self, context, submission_id):
    #     """ 获取用户的提交列表 """
    #     results = []
    #     next_id = -1
    #     # TODO: excludes 尚未实现
    #     while next_id:
    #         rows, next_id = self._query_submission(context, last_id=next_id)
    #         for row in rows[1:]:
    #             submission = self._parse_submission_row(context, row)
    #             results.append(submission)
    #             # print(submission.__dict__)
    #     return results

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

    def submit_problem(self, context, problem_id, language_id, code, contest_id=None):
        """
        :param context:
        :param problem_id:
        :param language_id: OJ 内部语言编号
        :param code:
        :param contest_id:
        :return:
        """
        # 校验输入的语言
        if not language_id:
            print('>>> 提交失败：语言编码为空')
            return None
        # 实际提交的 problemID 和题目的 problem_id 不一致，需要先抓过来转换一下
        resp = context.session.get(urljoin(
            self.homepage,
            r'/onlinejudge/showProblem.do?problemCode={}'.format(problem_id)))
        print('>>> origin problem_id = {}'.format(problem_id))
        problem_id = re.findall(r'/onlinejudge/submit\.do\?problemId=(\d+)',
                                resp.content.decode(self.charset))[0]
        print('>>> actual problem_id = {}'.format(problem_id))
        # 提交代码
        resp = context.session.post(
            url=urljoin(self.homepage, '/onlinejudge/submit.do'),
            data=dict(
                problemId=problem_id,
                languageId=language_id,
                source=code,
            ),
        )
        soup = BeautifulSoup(resp.content.decode(self.charset), 'lxml')
        # print(soup)
        submission_id = soup.select_one(r'#content_body font[color="red"]').text
        print('>>> submission_id: {}'.format(submission_id))
        # 获取结果
        retry = 10
        while True:
            rows, next_id = self._query_submission(
                context, id_end=submission_id, id_start=submission_id)
            # print(rows, next_id)
            # print(rows[0].select_one('.judgeReplyOther').text.strip())
            submission = self._parse_submission_row(context, rows[0])
            retry -= 1
            if submission.result or not retry:
                break
            from time import sleep
            sleep(11 - retry)
        return submission
