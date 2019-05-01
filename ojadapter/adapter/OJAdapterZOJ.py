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

    def download_problem(self, problem_id, contest_id=None):
        html = request_text(self.get_problem_url(problem_id, contest_id))
        problem = self.parse_problem(html)
        problem.id = problem_id
        problem.contest_id = contest_id
        return problem


