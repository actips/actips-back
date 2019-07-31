# from django.test import TestCase, SimpleTestCase
from unittest import TestCase

from .adapter import *


class TestAdapterCodeforces(TestCase):

    def __init__(self, *args, **kwargs):
        self.adapter = OJAdapterCodeforces()
        super().__init__(*args, **kwargs)

    def test_01_get_all_contest_numbers(self):
        print('输出所有的站内比赛编号')
        print(self.adapter.get_all_contest_numbers())

    def test_02_get_all_problem_numbers(self):
        print('输出所有的站内题目编号')
        print(self.adapter.get_all_problem_numbers())

    def test_03_get_problem_url(self):
        # 题目编号不带数字
        url = self.adapter.get_problem_url('1193A')
        dom = request_dom(url)
        self.assertEqual(dom.select('div.title')[0].text, 'A. Amusement Park')
        # 题目编号带数字
        url = self.adapter.get_problem_url('1196D2')
        dom = request_dom(url)
        self.assertEqual(dom.select('div.title')[0].text, 'D2. RGB Substring (hard version)')

    # def test_04_get_contest_problem_url(self):
    #     url = self.adapter.get_problem_url('2056', '131')
    #     dom = request_dom(url)
    #     self.assertEqual(dom.select('span.bigProblemTitle')[0].text, 'LED Display')
    def test_04_pdf_problem_parser(self):
        self.adapter.download_problem('180A')

    def test_05_parse_problem(self):
        # 后面抓题过来每一道卡住的都要加进测试
        # html = request_text(self.adapter.get_problem_url('1188A2'))
        # problem = self.adapter.parse_problem(html)
        # self.assertEqual(problem.title, 'Add on a Tree: Revolution')
        # self.assertEqual(problem.time_limit, 1000)
        # self.assertEqual(problem.memory_limit, 256 * 1024)
        # self.assertFalse(problem.is_special_judge)
        # self.assertTrue(problem.description.startswith('**Note that'))
        # self.assertTrue(problem.description.endswith('twice.'))
        # self.assertTrue(problem.input_specification.startswith('The first line'))
        # self.assertTrue(problem.input_specification.endswith('and even**.'))
        # self.assertTrue(problem.output_specification.startswith('If there aren\'t'))
        # self.assertTrue(problem.output_specification.endswith('above.'))
        # self.assertEqual(len(problem.input_samples), 2)
        # self.assertEqual(problem.input_samples[0], '5\n1 2 2\n2 3 4\n3 4 10\n3 5 18')
        # self.assertEqual(problem.input_samples[1], '6\n1 2 6\n1 3 8\n1 4 12\n2 5 2\n2 6 4')
        # self.assertEqual(len(problem.output_samples), 2)
        # self.assertEqual(problem.output_samples[0], 'NO')
        # self.assertEqual(problem.output_samples[1], 'YES\n4\n3 6 1\n4 6 3\n3 4 7\n4 5 2')
        # 鹅语的题目：524A 524B 675D 929A-E
        html = request_text(self.adapter.get_problem_url('929A'))
        problem = self.adapter.parse_problem(html)

    def test_06_download_problem(self):
        problem = self.adapter.download_problem('1184A3')
        problem.print()
        self.assertEqual(problem.title, 'Heidi Learns Hashing (Hard)')
        self.assertEqual(problem.id, '1184A3')
        self.assertEqual(problem.contest_id, '1184')

#     def test_07_get_user_solved_problem_list(self):
#         context = self.adapter.get_platform_user_context()
#         solved_problems_ids = self.adapter.get_user_solved_problem_list(context)
#         print(solved_problems_ids)
#         # 官方平台号交了这两道题，当做单元测试的 stub
#         self.assertIn('1001', solved_problems_ids)
#         self.assertIn('1654', solved_problems_ids)
#
#     def test_08_get_user_context_by_http_client(self):
#         context = self.adapter.get_platform_user_context()
#         cookies = dict(context.session.cookies)
#         headers = dict(context.session.headers)
#         context = self.adapter.get_user_context_by_http_client(cookies, headers)
#         solved_problems_ids = self.adapter.get_user_solved_problem_list(context)
#         print(solved_problems_ids)
#         self.assertTrue(self.adapter.check_context_validity(context))
#
#     def test_09_oj_login_session(self):
#         context = self.adapter.get_platform_user_context()
#         self.assertEqual(context.session.cookies['oj_handle'], self.adapter.platform_username)
#         self.assertEqual(context.session.cookies['oj_password'], '"{}"'.format(self.adapter.platform_password))
#
#     def test_10_oj_get_submission_list(self):
#         context = self.adapter.get_platform_user_context()
#         submissions = self.adapter.get_user_submission_list(context)
#         for sub in submissions:
#             print(sub.__dict__)
#         # context = self.adapter.get_user_context_by_user_and_password('fish_ball', '111111')
#         # submissions = self.adapter.get_user_submission_list(context)
#
#     def test_11_oj_submit_problem(self):
#         context = self.adapter.get_platform_user_context()
#         from ojadapter.entity.Submission import Submission
#         code = """
# #include <iostream>
# using namespace std;
# int main() {
#   int a, b;
#   while(cin >> a >> b) {
#     cout << a + b << endl;
#   }
#   return 0;
# }"""
#         submission = self.adapter.submit_problem(context, 1010, Submission.LANGUAGE_GPP, code)
#         print(submission.__dict__)
#         self.assertEqual(submission.result, Submission.RESULT_WRONG_ANSWER)
#         from time import sleep
#         print('wait for 10 seconds, to avoid "too fast" result')
#         sleep(10)  # Or you will get a "Submit too fast" result
#         submission = self.adapter.submit_problem(context, 1001, Submission.LANGUAGE_GPP, code)
#         print(submission.__dict__)
#         self.assertEqual(submission.result, Submission.RESULT_ACCEPTED)
