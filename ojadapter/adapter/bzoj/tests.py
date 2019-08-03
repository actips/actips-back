# from django.test import TestCase, SimpleTestCase
from unittest import TestCase

from .adapter import *


class TestAdapterBZOJ(TestCase):

    def __init__(self, *args, **kwargs):
        self.adapter = OJAdapterBZOJ()
        super().__init__(*args, **kwargs)

    # def test_01_get_all_contest_numbers(self):
    #     print('输出所有的站内比赛编号')
    #     print(self.adapter.get_all_contest_numbers())

    def test_02_get_all_problem_numbers(self):
        print('输出所有的站内题目编号')
        numbers = self.adapter.get_all_problem_numbers()
        print(numbers)
        # 有效题数在 2000-1000 之间
        self.assertGreater(len(numbers), 2000)
        self.assertLess(len(numbers), 10000)
        self.assertEqual(numbers[0], 1000)

    def test_03_get_problem_url(self):
        url = self.adapter.get_problem_url('1000')
        dom = request_dom(url)
        self.assertEqual(dom.select_one('center > h2').text, '1000: A+B Problem')

    # def test_04_pdf_problem_parser(self):
    #     problem = self.adapter.download_problem('1001')

    def test_05_parse_problem(self):
        # 后面抓题过来每一道卡住的都要加进测试
        problem = self.adapter.download_problem('1001')
        self.assertEqual(problem.title, '[BeiJing2006]狼抓兔子')
        self.assertEqual(problem.time_limit, 15000)
        self.assertEqual(problem.memory_limit, 162 * 1024)
        self.assertFalse(problem.is_special_judge)
        self.assertTrue(problem.description.startswith('现在小朋友们'))
        self.assertTrue(problem.description.endswith('喜羊羊麻烦.'))
        self.assertTrue(problem.input_specification.startswith('第一行为N,M.'))
        self.assertTrue(problem.input_specification.endswith('不超过10M'))
        self.assertTrue(problem.output_specification.startswith('输出一个整数'))
        self.assertTrue(problem.output_specification.endswith('最小数量.'))
        self.assertEqual(len(problem.input_samples), 1)
        self.assertEqual(problem.input_samples[0], '3 4\n5 6 4\n4 3 1\n7 5 3\n5 6 7 8\n8 7 6 5\n5 5 5\n6 6 6')
        self.assertEqual(len(problem.output_samples), 1)
        self.assertEqual(problem.output_samples[0], '14')
        # 1017 有些软换行需要处理掉，不然会在不应该的地方被分段
        problem = self.adapter.download_problem('1017')
        problem.print()
        # 5509 这个有 pdf 内链，有条件还是抓下来。
        # 不过还一堆没有描述的问题，这个还是放弃执念吧。

    # def test_06_download_problem(self):
    #     problem = self.adapter.download_problem('1184A3')
    #     problem.print()
    #     self.assertEqual(problem.title, 'Heidi Learns Hashing (Hard)')
    #     self.assertEqual(problem.id, '1184A3')
    #     self.assertEqual(problem.contest_id, '1184')
    #
    def test_07_get_user_solved_problem_list(self):
        context = self.adapter.get_platform_user_context()
        solved_problems_ids = self.adapter.get_user_solved_problem_list(context)
        print(solved_problems_ids)
        # 官方平台号交了这两道题，当做单元测试的 stub
        self.assertIn('1000', solved_problems_ids)
        self.assertNotIn('1654', solved_problems_ids)

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
        context = self.adapter.get_platform_user_context()
        submissions = self.adapter.get_user_submission_list(context)
        for sub in submissions:
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
        self.assertEqual(submission.result, Submission.RESULT_OUTPUT_LIMIT_EXCEED)
        from time import sleep
        print('wait for 10 seconds, to avoid "too fast" result')
        sleep(11)  # Or you will get a "Submit too fast" result
        submission = self.adapter.submit_problem(
            context, 1000, self.adapter.get_language_id_by_language(Submission.LANGUAGE_CPP), code)
        print(submission.__dict__)
        self.assertEqual(submission.result, Submission.RESULT_ACCEPTED)
