# from django.test import TestCase, SimpleTestCase
from unittest import TestCase

from .adapter import *


class TestAdapterHDOJ(TestCase):

    def __init__(self, *args, **kwargs):
        self.adapter = OJAdapterHDOJ()
        super().__init__(*args, **kwargs)

    # def test_01_get_all_contest_numbers(self):
    #     print('输出所有的站内比赛编号')
    #     print(self.adapter.get_all_contest_numbers())

    def test_02_get_all_problem_numbers(self):
        print('输出所有的站内题目编号')
        numbers = self.adapter.get_all_problem_numbers()
        print(numbers)
        # 有效题数在 5000-1000 之间
        self.assertGreater(len(numbers), 5000)
        self.assertLess(len(numbers), 10000)
        self.assertEqual(numbers[0], '1000')

    def test_03_get_problem_url(self):
        url = self.adapter.get_problem_url('1005')
        dom = request_dom(url, self.adapter.charset)
        self.assertEqual(dom.select_one('h1').text, 'Number Sequence')
        # 来个中文的
        url = self.adapter.get_problem_url('6411')
        dom = request_dom(url, self.adapter.charset)
        self.assertEqual(dom.select_one('h1').text, '带劲的and和')

    # def test_04_pdf_problem_parser(self):
    #     problem = self.adapter.download_problem('1001')

    def test_05_parse_problem(self):
        # 后面抓题过来每一道卡住的都要加进测试
        problem = self.adapter.download_problem('6411')
        self.assertEqual(problem.title, '带劲的and和')
        self.assertEqual(problem.time_limit, 1000)
        self.assertEqual(problem.memory_limit, 65536)
        self.assertTrue(problem.description.startswith('度度熊专门'))
        self.assertTrue(problem.description.endswith('后输出。'))
        self.assertTrue(problem.input_specification.startswith('第一行一个数，'))
        self.assertTrue(problem.input_specification.endswith('1000$$$。'))
        self.assertTrue(problem.output_specification.startswith('每组数据输出一行'))
        self.assertTrue(problem.output_specification.endswith('带劲的and和。'))
        self.assertEqual(len(problem.input_samples), 1)
        self.assertEqual(problem.input_samples[0], '1\n5 5\n3 9 4 8 9 \n2 1\n1 3\n2 1\n1 2\n5 2')
        self.assertEqual(len(problem.output_samples), 1)
        self.assertEqual(problem.output_samples[0], '99')
        self.assertFalse(problem.is_special_judge)
        # 1522 是 Special Judge
        problem = self.adapter.download_problem('1522')
        self.assertEqual(problem.title, 'Marriage is Stable')
        self.assertTrue(problem.is_special_judge)
        # 1023 在 Sample Output 里面整了个 Hint
        problem = self.adapter.download_problem('1023')
        self.assertEqual(problem.title, 'Train Problem II')
        self.assertEqual(len(problem.output_samples), 1)
        self.assertEqual(problem.output_samples[0], '1\n2\n5\n16796')
        self.assertEqual(problem.extra_description,
                         'The result will be very large, so you may not process it by 32-bit integers.')
        # 6621 报编码错误（因为有非法字符）
        problem = self.adapter.download_problem('6621')

    # def test_06_download_problem(self):
    #     problem = self.adapter.download_problem('1184A3')
    #     problem.print()
    #     self.assertEqual(problem.title, 'Heidi Learns Hashing (Hard)')
    #     self.assertEqual(problem.id, '1184A3')
    #     self.assertEqual(problem.contest_id, '1184')

    def test_07_get_user_solved_problem_list(self):
        # context = self.adapter.get_platform_user_context()
        context = self.adapter.get_user_context_by_user_and_password('fish_ball', '111111')
        solved_problems_ids = self.adapter.get_user_solved_problem_list(context)
        unsolved_problems_ids = self.adapter.get_user_failed_problem_list(context)
        # 官方平台号交了这两道题，当做单元测试的 stub
        self.assertIn('1000', solved_problems_ids)
        self.assertNotIn('2449', solved_problems_ids)
        self.assertNotIn('1000', unsolved_problems_ids)
        self.assertIn('4830', unsolved_problems_ids)

    def test_08_get_user_context_by_http_client(self):
        context = self.adapter.get_platform_user_context()
        cookies = dict(context.session.cookies)
        headers = dict(context.session.headers)
        context = self.adapter.get_user_context_by_http_client(cookies, headers)
        # solved_problems_ids = self.adapter.get_user_solved_problem_list(context)
        # print(solved_problems_ids)
        self.assertTrue(self.adapter.check_context_validity(context))

    def test_09_oj_login_session(self):
        context = self.adapter.get_platform_user_context()
        # self.assertEqual(context.session.cookies['oj_handle'], self.adapter.platform_username)
        # self.assertEqual(context.session.cookies['oj_password'], '"{}"'.format(self.adapter.platform_password))
        self.assertTrue(self.adapter.check_context_validity(context))
        self.assertEqual(self.adapter._get_current_handle(context), self.adapter.platform_username)

    def test_10_oj_get_submission_list(self):
        context = self.adapter.get_user_context_by_user_and_password('fish_ball', '111111')
        # context = self.adapter.get_platform_user_context()
        submissions = self.adapter.get_user_submission_list(context)
        for sub in submissions:
            self.assertTrue(sub.language_id in {l['id'] for l in self.adapter.get_supported_languages()})
            self.assertTrue(sub.result)
            print(sub.__dict__)
        # context = self.adapter.get_user_context_by_user_and_password('fish_ball', '111111')
        # submissions = self.adapter.get_user_submission_list(context)

    def test_11_oj_submit_problem(self):
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
        submission = self.adapter.submit_problem(
            context, 1010, self.adapter.get_language_id_by_language(Submission.LANGUAGE_CPP), code)
        self.assertEqual(submission.result, Submission.RESULT_WRONG_ANSWER)
        self.assertEqual(submission.language_id, 0)
        from time import sleep
        print('wait for 10 seconds, to avoid "too fast" result')
        sleep(11)  # Or you will get a "Submit too fast" result
        submission = self.adapter.submit_problem(
            context, 1000, self.adapter.get_language_id_by_language(Submission.LANGUAGE_CPP), code)
        print(submission.__dict__)
        self.assertEqual(submission.result, Submission.RESULT_ACCEPTED)
