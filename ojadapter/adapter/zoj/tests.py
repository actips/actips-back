# from django.test import TestCase, SimpleTestCase
from unittest import TestCase

from .adapter import *


class TestAdapterZOJ(TestCase):

    def __init__(self, *args, **kwargs):
        self.adapter = OJAdapterZOJ()
        super().__init__(*args, **kwargs)

    def test_01_get_all_contest_numbers(self):
        print('输出所有的站内比赛编号')
        print(self.adapter.get_all_contest_numbers())

    def test_02_get_all_problem_numbers(self):
        print('输出所有的站内题目编号')
        print(self.adapter.get_all_problem_numbers())

    def test_03_get_problem_url(self):
        url = self.adapter.get_problem_url('1001')
        dom = request_dom(url)
        self.assertEqual(dom.select('span.bigProblemTitle')[0].text, 'A + B Problem')

    def test_04_get_contest_problem_url(self):
        url = self.adapter.get_problem_url('2056', '131')
        dom = request_dom(url)
        self.assertEqual(dom.select('span.bigProblemTitle')[0].text, 'LED Display')

    def test_05_parse_problem(self):
        # 后面抓题过来每一道卡住的都要加进测试
        # 拿一道 1005 Special Judge 测一下
        html = request_text(self.adapter.get_problem_url(1005))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Jugs')
        self.assertEqual(problem.time_limit, 2)
        self.assertEqual(problem.memory_limit, 65536)
        self.assertTrue(problem.is_special_judge)
        self.assertTrue(problem.description.startswith('In the movie'))
        self.assertTrue(problem.description.endswith('solution.'))
        self.assertTrue(problem.input_specification.startswith('Input to your'))
        self.assertTrue(problem.input_specification.endswith('another.'))
        self.assertTrue(problem.output_specification.startswith('Output from your'))
        self.assertTrue(problem.output_specification.endswith('spaces.'))
        self.assertEqual(problem.input_samples[0], '3 5 4\n5 7 3')
        self.assertEqual(problem.output_samples[0],
                         'fill B\npour B A\nempty A\npour B A\nfill B\npour B A\nsuccess\n'
                         'fill A\npour A B\nfill A\npour A B\nempty B\npour A B\nsuccess')
        self.assertEqual(problem.author, '')
        self.assertEqual(problem.source, 'Zhejiang University Local Contest 2001')
        # 再抓道比较新的 4067
        html = request_text(self.adapter.get_problem_url(4067))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Books')
        self.assertEqual(problem.time_limit, 1)
        self.assertEqual(problem.memory_limit, 65536)
        self.assertTrue(not problem.is_special_judge)
        self.assertTrue(problem.description.startswith('DreamGrid went'))
        self.assertTrue(problem.description.endswith('$m$.'))
        self.assertTrue(problem.input_specification.startswith('There are multiple'))
        self.assertTrue(problem.input_specification.endswith('$10^6$.'))
        self.assertTrue(problem.output_specification.startswith('For each'))
        self.assertTrue(problem.output_specification.endswith('may take.'))
        self.assertEqual(problem.input_samples[0],
                         '4\n4 2\n1 2 4 8\n4 0\n100 99 98 97\n2 2\n10000 10000\n5 3\n0 0 0 0 1')
        self.assertEqual(problem.output_samples[0], '6\n96\nRichman\nImpossible')
        self.assertEqual(problem.author, 'CHEN, Shihan')
        self.assertEqual(problem.source, 'The 2018 ACM-ICPC Asia Qingdao Regional Contest')
        # 再抓到完事后还插话的 4022
        html = request_text(self.adapter.get_problem_url(4022))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Honorifics')
        self.assertEqual(problem.time_limit, 2)
        self.assertEqual(problem.memory_limit, 65536)
        self.assertTrue(problem.is_special_judge)
        self.assertTrue(problem.description.startswith('An honorific'))
        self.assertTrue(problem.description.endswith('the test.'))
        self.assertTrue(problem.extra_description.startswith('#### Data'))
        self.assertTrue(problem.extra_description.endswith('yourself.'))
        self.assertTrue(problem.input_specification.startswith('For the formal test'))
        self.assertTrue(problem.input_specification.endswith('exceed 20.'))
        self.assertTrue(problem.output_specification.startswith('For each'))
        self.assertTrue(problem.output_specification.endswith('at least.'))
        self.assertEqual(problem.input_samples[0],
                         '7\nFuzii Mina\nNakamoto Yuuta\nSong Junggi\nHirai Momo\nSeonu Jeonga\nGong Yu\nBang Mina')
        self.assertEqual(problem.output_samples[0],
                         'Fuzii Mina-san\nNakamoto Yuuta-san\nSong Junggi-ssi\nHirai Momo-san\n'
                         'Seonu Jeonga-ssi\nGong Yu-ssi\nBang Mina-ssi')
        self.assertEqual(problem.author, 'ZHOU, Yuchen')
        self.assertEqual(problem.source, 'The 18th Zhejiang University Programming Contest Sponsored by TuSimple')
        # 抓一道比赛内题目
        html = request_text(self.adapter.get_problem_url(4728, 338))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Choir II')
        self.assertEqual(problem.time_limit, 5)
        self.assertEqual(problem.memory_limit, 65536)
        self.assertEqual(problem.is_special_judge, False)
        self.assertTrue(problem.description.startswith('After the'))
        self.assertTrue(problem.description.endswith('divided way.'))
        self.assertEqual(problem.extra_description, '')
        self.assertTrue(problem.input_specification.startswith('The input file'))
        self.assertTrue(problem.input_specification.endswith('characters.'))
        self.assertTrue(problem.output_specification.startswith('For each'))
        self.assertTrue(problem.output_specification.endswith('can get.'))
        self.assertEqual(problem.input_samples[0],
                         '3 2\nKit: I love KityKityMityMity\nSam: Kity is a QmOnkey\n'
                         'Bob: I don\'t like anyone.\nKity: Sam is a so smart.\nMity: Sam is good.')
        self.assertEqual(problem.output_samples[0], '34')
        self.assertEqual(problem.author, 'LI, Fei')
        self.assertEqual(problem.source, '')

    def test_05_download_problem(self):
        problem = self.adapter.download_problem(4728, 338)
        problem.print()
        self.assertEqual(problem.title, 'Choir II')
        self.assertEqual(problem.id, 4728)
        self.assertEqual(problem.contest_id, 338)
        problem = self.adapter.download_problem(4022)
        problem.print()
        self.assertEqual(problem.title, 'Honorifics')
        self.assertEqual(problem.id, 4022)
        self.assertIsNone(problem.contest_id)

    def test_06_get_user_solved_problem_list(self):
        context = self.adapter.get_platform_user_context()
        solved_problems_ids = self.adapter.get_user_solved_problem_list(context)
        print(solved_problems_ids)
        # 官方平台号交了这两道题，当做单元测试的 stub
        self.assertIn('1001', solved_problems_ids)
        self.assertIn('1654', solved_problems_ids)

    def test_07_get_user_context_by_http_client(self):
        context = self.adapter.get_platform_user_context()
        cookies = dict(context.session.cookies)
        headers = dict(context.session.headers)
        context = self.adapter.get_user_context_by_http_client(cookies, headers)
        solved_problems_ids = self.adapter.get_user_solved_problem_list(context)
        print(solved_problems_ids)
        self.assertTrue(self.adapter.check_context_validity(context))

    def test_08_oj_login_session(self):
        context = self.adapter.get_platform_user_context()
        self.assertEqual(context.session.cookies['oj_handle'], self.adapter.platform_username)
        self.assertEqual(context.session.cookies['oj_password'], '"{}"'.format(self.adapter.platform_password))

    def test_09_oj_get_submission_list(self):
        context = self.adapter.get_platform_user_context()
        submissions = self.adapter.get_user_submission_list(context)
        for sub in submissions:
            print(sub.__dict__)
        # context = self.adapter.get_user_context_by_user_and_password('fish_ball', '111111')
        # submissions = self.adapter.get_user_submission_list(context)

    def test_10_oj_submit_problem(self):
        context = self.adapter.get_platform_user_context()
        from ojadapter.entity.Submission import Submission
        code = """
#include <iostream>
using namespace std;
int main() {
  int a, b;
  while(cin >> a >> b) {
    cout << a + b << endl;
  }
  return 0;
}"""
        submission = self.adapter.submit_problem(context, 1010, Submission.LANGUAGE_GPP, code)
        print(submission.__dict__)
        self.assertEqual(submission.result, Submission.RESULT_WRONG_ANSWER)
        from time import sleep
        print('wait for 10 seconds, to avoid "too fast" result')
        sleep(10)  # Or you will get a "Submit too fast" result
        submission = self.adapter.submit_problem(context, 1001, Submission.LANGUAGE_GPP, code)
        print(submission.__dict__)
        self.assertEqual(submission.result, Submission.RESULT_ACCEPTED)
