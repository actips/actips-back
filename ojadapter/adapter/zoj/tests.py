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
        assert dom.select('span.bigProblemTitle')[0].text == 'A + B Problem'

    def test_04_get_contest_problem_url(self):
        url = self.adapter.get_problem_url('2056', '131')
        dom = request_dom(url)
        assert dom.select('span.bigProblemTitle')[0].text == 'LED Display'

    def test_05_parse_problem(self):
        # 后面抓题过来每一道卡住的都要加进测试
        # 拿一道 1005 Special Judge 测一下
        html = request_text(self.adapter.get_problem_url(1005))
        problem = self.adapter.parse_problem(html)
        assert problem.title == 'Jugs'
        assert problem.time_limit == 2
        assert problem.memory_limit == 65536
        assert problem.is_special_judge
        assert problem.description.startswith('In the movie')
        assert problem.description.endswith('solution.')
        assert problem.input_specification.startswith('Input to your')
        assert problem.input_specification.endswith('another.')
        assert problem.output_specification.startswith('Output from your')
        assert problem.output_specification.endswith('spaces.')
        assert problem.input_samples[0] == '3 5 4\n5 7 3'
        assert problem.output_samples[0] == 'fill B\npour B A\nempty A\npour B A\nfill B\npour B A\nsuccess\n' \
                                            'fill A\npour A B\nfill A\npour A B\nempty B\npour A B\nsuccess'
        assert problem.author == ''
        assert problem.source == 'Zhejiang University Local Contest 2001'
        # 再抓道比较新的 4067
        html = request_text(self.adapter.get_problem_url(4067))
        problem = self.adapter.parse_problem(html)
        assert problem.title == 'Books'
        assert problem.time_limit == 1
        assert problem.memory_limit == 65536
        assert not problem.is_special_judge
        assert problem.description.startswith('DreamGrid went')
        assert problem.description.endswith('$m$.')
        assert problem.input_specification.startswith('There are multiple')
        assert problem.input_specification.endswith('$10^6$.')
        assert problem.output_specification.startswith('For each')
        assert problem.output_specification.endswith('may take.')
        assert problem.input_samples[0] == '4\n4 2\n1 2 4 8\n4 0\n100 99 98 97\n2 2\n10000 10000\n5 3\n0 0 0 0 1'
        assert problem.output_samples[0] == '6\n96\nRichman\nImpossible'
        assert problem.author == 'CHEN, Shihan'
        assert problem.source == 'The 2018 ACM-ICPC Asia Qingdao Regional Contest'
        # 再抓到完事后还插话的 4022
        html = request_text(self.adapter.get_problem_url(4022))
        problem = self.adapter.parse_problem(html)
        assert problem.title == 'Honorifics'
        assert problem.time_limit == 2
        assert problem.memory_limit == 65536
        assert problem.is_special_judge
        assert problem.description.startswith('An honorific')
        assert problem.description.endswith('the test.')
        assert problem.extra_description.startswith('#### Data')
        assert problem.extra_description.endswith('yourself.')
        assert problem.input_specification.startswith('For the formal test')
        assert problem.input_specification.endswith('exceed 20.')
        assert problem.output_specification.startswith('For each')
        assert problem.output_specification.endswith('at least.')
        assert problem.input_samples[0] == \
               '7\nFuzii Mina\nNakamoto Yuuta\nSong Junggi\nHirai Momo\nSeonu Jeonga\nGong Yu\nBang Mina'
        assert problem.output_samples[0] == \
               'Fuzii Mina-san\nNakamoto Yuuta-san\nSong Junggi-ssi\nHirai Momo-san\n' \
               'Seonu Jeonga-ssi\nGong Yu-ssi\nBang Mina-ssi'
        assert problem.author == 'ZHOU, Yuchen'
        assert problem.source == 'The 18th Zhejiang University Programming Contest Sponsored by TuSimple'
        # 抓一道比赛内题目
        html = request_text(self.adapter.get_problem_url(4728, 338))
        problem = self.adapter.parse_problem(html)
        assert problem.title == 'Choir II'
        assert problem.time_limit == 5
        assert problem.memory_limit == 65536
        assert problem.is_special_judge == False
        assert problem.description.startswith('After the')
        assert problem.description.endswith('divided way.')
        assert problem.extra_description == ''
        assert problem.input_specification.startswith('The input file')
        assert problem.input_specification.endswith('characters.')
        assert problem.output_specification.startswith('For each')
        assert problem.output_specification.endswith('can get.')
        assert problem.input_samples[0] == \
               '3 2\nKit: I love KityKityMityMity\nSam: Kity is a QmOnkey\n' \
               'Bob: I don\'t like anyone.\nKity: Sam is a so smart.\nMity: Sam is good.'
        assert problem.output_samples[0] == '34'
        assert problem.author == 'LI, Fei'
        assert problem.source == ''

    def test_05_download_problem(self):
        problem = self.adapter.download_problem(4728, 338)
        problem.print()
        assert problem.title == 'Choir II'
        assert problem.id == 4728
        assert problem.contest_id == 338
        problem = self.adapter.download_problem(4022)
        problem.print()
        assert problem.title == 'Honorifics'
        assert problem.id == 4022
        assert problem.contest_id is None

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
        # context = self.adapter.get_user_context_by_user_and_password('fish_ball', '111111')
        # submissions = self.adapter.get_user_submission_list(context)

