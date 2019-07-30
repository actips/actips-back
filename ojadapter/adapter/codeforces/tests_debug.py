# from django.test import TestCase, SimpleTestCase
from unittest import TestCase

from .adapter import *


class TestDebugAdapterZOJ(TestCase):

    def __init__(self, *args, **kwargs):
        self.adapter = OJAdapterZOJ()
        super().__init__(*args, **kwargs)

    def test_05_parse_problem(self):
        # 后面抓题过来每一道卡住的都要加进测试
        # 1134-1141 规矩变了，特殊处理的
        html = request_text(self.adapter.get_problem_url(1137))
        problem = self.adapter.parse_problem(html)
        self.assertEqual(problem.input_samples[0],
                         '7  \n0: (3) 4 5 6  \n1: (2) 4 6  \n2: (0)  \n3: (0)  \n4: (2) 0 1  \n'
                         '5: (1) 0  \n6: (2) 0 1  \n3  \n0: (2) 1 2  \n1: (1) 0  \n2: (1) 0')
        self.assertEqual(problem.output_samples[0],
                         '5  \n2')
