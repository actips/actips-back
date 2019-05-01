import re

from bs4 import BeautifulSoup
from html2text import html2text

from ojadapter.entity.Problem import Problem
from ..utils import request_dom, request_text
from .OJAdapterBase import OJAdapterBase
from urllib.parse import urljoin


class OJAdapterZOJ(OJAdapterBase):
    code = 'ZOJ'
    homepage = r'http://acm.zju.edu.cn'

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
        print(content)
        parser = re.compile(
            r'<hr/>(?:.|\n)+<hr/>(?P<description>(?:.|\n)+)'
            r'(?:(?:<p><b>|<h4>)Input(?:</h4>|</b>[\s\n]*</p>))(?P<input_specification>(?:.|\n)+)'
            r'(?:(?:<p><b>|<h4>)Output(?:</h4>|</b>[\s\n]*</p>))(?P<output_specification>(?:.|\n)+)'
            r'(?:<h4>Sample Input</h4>[\s\n]*<pre>(?P<input_samples>(?:.|\n)+)</pre>[\s\n]*)'
            r'(?:<h4>Sample Output</h4>[\s\n]*<pre>(?P<output_samples>(?:.|\n)+)</pre>[\s\n]*)'
            r'<hr/>[\s\n]*'
            r'(?:Author:\s+<strong>(?P<author>.+)</strong><br/>[\s\n]+)?'
            r'(?:Source:\s+<strong>(?P<source>.+)</strong><br/>[\s\n]+)'
            r'<center>'
            , re.MULTILINE
        )
        data = next(parser.finditer(content)).groupdict()
        problem.description = html2text(data.get('description') or '').strip()
        problem.input_specification = html2text(data.get('input_specification') or '').strip()
        problem.output_specification = html2text(data.get('output_specification') or '').strip()
        problem.input_samples = [data.get('input_samples', '').strip()]
        problem.output_samples = [data.get('output_samples', '').strip()]
        problem.author = data.get('author', '').strip()
        problem.source = data.get('source', '').strip()

        # print(data)
        # [print('\n\n<<<<{}>>>>\n'.format(k), v) for k, v in data.items()]

        [print(k, '=', v) for k, v in problem.__dict__.items()]
        return problem

    # def get_content_from_body(self, content):
    # dom = BeautifulSoup(content, 'lxml')
    # return dom.select('.bigProblemTitle')[0].text

    # ======================== TESTCASE ==========================

    # def test_01_get_all_contest_numbers(self):
    #     print('输出所有的站内比赛编号')
    #     print(self.get_all_contest_numbers())
    #
    # def test_02_get_all_problem_numbers(self):
    #     print('输出所有的站内题目编号')
    #     print(self.get_all_problem_numbers())
    #
    # def test_03_get_problem_url(self):
    #     url = self.get_problem_url('1001')
    #     dom = request_dom(url)
    #     assert dom.select('span.bigProblemTitle')[0].text == 'A + B Problem'
    #
    # def test_04_get_contest_problem_url(self):
    #     url = self.get_problem_url('2056', '131')
    #     dom = request_dom(url)
    #     assert dom.select('span.bigProblemTitle')[0].text == 'LED Display'

    def test_05_parse_problem(self):
        # 后面抓题过来每一道卡住的都要加进测试
        # 拿一道 1005 Special Judge 测一下
        html = request_text(self.get_problem_url(1005))
        problem = self.parse_problem(html)
        # assert problem.title == 'Jugs'
        # assert problem.time_limit == 2
        # assert problem.memory_limit == 65536
        # assert problem.is_special_judge
        # assert problem.description.startswith('In the movie')
        # assert problem.description.endswith('solution.')
        # assert problem.input_specification.startswith('Input to your')
        # assert problem.input_specification.endswith('another.')
        # assert problem.output_specification.startswith('Output from your')
        # assert problem.output_specification.endswith('spaces.')
        # assert problem.input_samples[0] == '3 5 4\n5 7 3'
        # assert problem.output_samples[0] == 'fill B\npour B A\nempty A\npour B A\nfill B\npour B A\nsuccess\n' \
        #                                     'fill A\npour A B\nfill A\npour A B\nempty B\npour A B\nsuccess'
        # assert problem.source == 'Zhejiang University Local Contest 2001'
        # 再抓道比较新的 4067
        html = request_text(self.get_problem_url(4067))
        problem = self.parse_problem(html)
        # 再抓到完事后还插话的 4022

    # def test_05_get_title_from_body(self):
    #     url = self.get_problem_url('1001')
    #     content = request_text(url)
    #     assert self.get_title_from_body(content) == 'A + B Problem'
    #     url = self.get_problem_url('2056', '131')
    #     content = request_text(url)
    #     assert self.get_title_from_body(content) == 'LED Display'
    #
    # def test_06_get_content_from_body(self):
