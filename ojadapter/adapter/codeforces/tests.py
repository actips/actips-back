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
        # TODO: 1076-1081 搞不定
        # 1134-1141 规矩变了，特殊处理的
        html = request_text(self.adapter.get_problem_url(1137))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.input_samples[0],
                         '7  \n0: (3) 4 5 6  \n1: (2) 4 6  \n2: (0)  \n3: (0)  \n4: (2) 0 1  \n'
                         '5: (1) 0  \n6: (2) 0 1  \n3  \n0: (2) 1 2  \n1: (1) 0  \n2: (1) 0')
        self.assertEqual(problem.output_samples[0],
                         '5  \n2')
        # 1114 这种格式很有代表性
        html = request_text(self.adapter.get_problem_url(1114))
        problem = self.adapter.parse_problem(html)
        self.assertTrue(problem.input_specification.startswith('Input will be in the form'))
        self.assertTrue(problem.input_specification.endswith('hexagons.'))
        self.assertTrue(problem.output_specification.startswith('For each'))
        self.assertTrue(problem.output_specification.endswith('centimeters.'))
        self.assertEqual(problem.input_samples[0],
                         '1.0 -3.2 2.2 3.3 0\n9 1 4 5 1\n0.1 .09 0 .21 0\n0 0 0 0 0')
        self.assertEqual(problem.output_samples[0],
                         '7.737\n5.000\n0.526')
        # 1008 也是一特立独行的主
        html = request_text(self.adapter.get_problem_url(1008))
        problem = self.adapter.parse_problem(html)
        self.assertTrue(problem.description.startswith('Hart'))
        self.assertTrue(problem.description.endswith('on it.'))
        self.assertTrue(problem.input_specification.startswith('The input file consists'))
        self.assertTrue(problem.input_specification.endswith('data set.'))
        self.assertTrue(problem.output_specification.startswith('You should'))
        self.assertTrue(problem.output_specification.endswith('unacceptable.'))
        self.assertEqual(problem.input_samples[0],
                         '2  \n5 9 1 4  \n4 4 5 6  \n6 8 5 4  \n0 4 4 3  \n2  \n1 1 1 1  \n'
                         '2 2 2 2  \n3 3 3 3  \n4 4 4 4  \n0')
        self.assertEqual(problem.output_samples[0],
                         'Game 1: Possible\n\nGame 2: Impossible')
        # 2813 奇葩格式需要补刀
        html = request_text(self.adapter.get_problem_url(2813))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Linear Pachinko')
        self.assertEqual(problem.time_limit, 2000)
        self.assertEqual(problem.memory_limit, 65536)
        self.assertFalse(problem.is_special_judge)
        self.assertTrue(problem.description.startswith('This problem'))
        self.assertTrue(problem.description.endswith('61.111%.'))
        self.assertTrue(problem.input_specification.startswith('The input consists'))
        self.assertTrue(problem.input_specification.endswith('end of the input.'))
        self.assertTrue(problem.output_specification.startswith('For each machine,'))
        self.assertTrue(problem.output_specification.endswith('fractional part.'))
        self.assertEqual(problem.input_samples[0],
                         '/\\.|__/\\.\n_._/\\_|.__/\\./\\_\n...\n___\n./\\.\n_/\\_\n_|.|_|.|_|.|_\n____|_____\n#')
        self.assertEqual(problem.output_samples[0], '61\n53\n100\n0\n100\n50\n53\n10')
        self.assertEqual(problem.get_extra_info('source'), 'Mid-Central USA 2006')
        # 1001，大爷格式
        html = request_text(self.adapter.get_problem_url(1001))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'A + B Problem')
        self.assertEqual(problem.time_limit, 2000)
        self.assertEqual(problem.memory_limit, 65536)
        self.assertFalse(problem.is_special_judge)
        self.assertTrue(problem.description.startswith('Calculate'))
        self.assertTrue(problem.description.endswith('a + b'))
        self.assertTrue(problem.input_specification.startswith('The input will'))
        self.assertTrue(problem.input_specification.endswith('integers per line.'))
        self.assertTrue(problem.output_specification.startswith('For each'))
        self.assertTrue(problem.output_specification.endswith('in input.'))
        self.assertEqual(problem.input_samples[0], '1 5')
        self.assertEqual(problem.output_samples[0], '6')
        # 1002，格式很不一样
        html = request_text(self.adapter.get_problem_url(1002))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Fire Net')
        self.assertEqual(problem.time_limit, 2000)
        self.assertEqual(problem.memory_limit, 65536)
        self.assertFalse(problem.is_special_judge)
        self.assertTrue(problem.description.startswith('Suppose that'))
        self.assertTrue(problem.description.endswith('configuration.'))
        self.assertEqual(problem.input_specification, '')
        self.assertEqual(problem.output_specification, '')
        self.assertTrue(problem.input_samples[0].startswith('4\n'))
        self.assertTrue(problem.input_samples[0].endswith('....\n0'))
        self.assertEqual(problem.output_samples[0], '5\n1\n5\n2\n4')
        self.assertEqual(problem.get_extra_info('source'), 'Zhejiang University Local Contest 2001')
        # 3517，有 Contest 这个附加行
        html = request_text(self.adapter.get_problem_url(3517))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Tower VII')
        self.assertEqual(problem.time_limit, 5000)
        self.assertEqual(problem.memory_limit, 131024)
        self.assertFalse(problem.is_special_judge)
        self.assertTrue(problem.description.startswith('Once upon a time'))
        self.assertTrue(problem.description.endswith('sample output.'))
        self.assertTrue(problem.input_specification.startswith('There are'))
        self.assertTrue(problem.input_specification.endswith('ground floor.'))
        self.assertTrue(problem.output_specification.startswith('For each test case'))
        self.assertTrue(problem.output_specification.endswith('one line.'))
        self.assertEqual(problem.get_extra_info('author'), 'FAN, Yuzhe')
        self.assertEqual(problem.get_extra_info('contest'), 'ZOJ Monthly, July 2011')
        # 拿一道 1005 Special Judge 测一下
        html = request_text(self.adapter.get_problem_url(1005))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Jugs')
        self.assertEqual(problem.time_limit, 2000)
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
        self.assertIsNone(problem.get_extra_info('author'))
        self.assertEqual(problem.get_extra_info('source'), 'Zhejiang University Local Contest 2001')
        # 再抓道比较新的 4067
        html = request_text(self.adapter.get_problem_url(4067))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Books')
        self.assertEqual(problem.time_limit, 1000)
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
        self.assertEqual(problem.get_extra_info('author'), 'CHEN, Shihan')
        self.assertEqual(problem.get_extra_info('source'), 'The 2018 ACM-ICPC Asia Qingdao Regional Contest')
        # 再抓到完事后还插话的 4022
        html = request_text(self.adapter.get_problem_url(4022))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Honorifics')
        self.assertEqual(problem.time_limit, 2000)
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
        self.assertEqual(problem.get_extra_info('author'), 'ZHOU, Yuchen')
        self.assertEqual(problem.get_extra_info('source'), 'The 18th Zhejiang University Programming Contest Sponsored by TuSimple')
        # 抓一道比赛内题目
        html = request_text(self.adapter.get_problem_url(4728, 338))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.title, 'Choir II')
        self.assertEqual(problem.time_limit, 5000)
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
        self.assertEqual(problem.get_extra_info('author'), 'LI, Fei')
        self.assertIsNone(problem.get_extra_info('source'))

    def test_06_download_problem(self):
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

    def test_07_get_user_solved_problem_list(self):
        context = self.adapter.get_platform_user_context()
        solved_problems_ids = self.adapter.get_user_solved_problem_list(context)
        print(solved_problems_ids)
        # 官方平台号交了这两道题，当做单元测试的 stub
        self.assertIn('1001', solved_problems_ids)
        self.assertIn('1654', solved_problems_ids)

    def test_08_get_user_context_by_http_client(self):
        context = self.adapter.get_platform_user_context()
        cookies = dict(context.session.cookies)
        headers = dict(context.session.headers)
        context = self.adapter.get_user_context_by_http_client(cookies, headers)
        solved_problems_ids = self.adapter.get_user_solved_problem_list(context)
        print(solved_problems_ids)
        self.assertTrue(self.adapter.check_context_validity(context))

    def test_09_oj_login_session(self):
        context = self.adapter.get_platform_user_context()
        self.assertEqual(context.session.cookies['oj_handle'], self.adapter.platform_username)
        self.assertEqual(context.session.cookies['oj_password'], '"{}"'.format(self.adapter.platform_password))

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
        submission = self.adapter.submit_problem(context, 1010, Submission.LANGUAGE_GPP, code)
        print(submission.__dict__)
        self.assertEqual(submission.result, Submission.RESULT_WRONG_ANSWER)
        from time import sleep
        print('wait for 10 seconds, to avoid "too fast" result')
        sleep(10)  # Or you will get a "Submit too fast" result
        submission = self.adapter.submit_problem(context, 1001, Submission.LANGUAGE_GPP, code)
        print(submission.__dict__)
        self.assertEqual(submission.result, Submission.RESULT_ACCEPTED)
