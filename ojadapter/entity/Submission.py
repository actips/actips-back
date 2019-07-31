import pickle

import requests
import os
import os.path
from uuid import uuid4

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Submission(object):
    LANGUAGE_UNDEFINED = ''
    LANGUAGE_C = 'C'
    LANGUAGE_CPP = 'CPP'
    LANGUAGE_JAVA = 'JAVA'
    LANGUAGE_PYTHON2 = 'PYTHON2'
    LANGUAGE_PYTHON3 = 'PYTHON3'
    LANGUAGE_PASCAL = 'PASCAL'
    LANGUAGE_DELPHI = 'DELPHI'
    LANGUAGE_PERL = 'PERL'
    LANGUAGE_SCHEME = 'SCHEME'
    LANGUAGE_PHP = 'PHP'
    LANGUAGE_RUBY = 'RUBY'
    LANGUAGE_CSHARP = 'CSHARP'
    LANGUAGE_HASKELL = 'HASKELL'
    LANGUAGE_OCAML = 'OCAML'
    LANGUAGE_SCALA = 'SCALA'
    LANGUAGE_D = 'D'
    LANGUAGE_GO = 'GO'
    LANGUAGE_JAVASCRIPT = 'JAVASCRIPT'
    LANGUAGE_KOTLIN = 'KOTLIN'
    LANGUAGE_RUST = 'RUST'
    LANGUAGE_CLANG = 'CLANG'
    LANGUAGE_NODEJS = 'NODEJS'
    LANGUAGE_CHOICES = (
        (LANGUAGE_UNDEFINED, ''),
        (LANGUAGE_C, 'C'),
        (LANGUAGE_CPP, 'C++'),
        # (LANGUAGE_GCC, 'GCC'), => CPP
        # (LANGUAGE_GPP, 'G++'), => CPP
        # (LANGUAGE_CPP11, 'C++11'), => CPP
        (LANGUAGE_JAVA, 'Java'),
        (LANGUAGE_PYTHON2, 'Python2'),
        (LANGUAGE_PYTHON3, 'Python3'),
        (LANGUAGE_PASCAL, 'Pascal'),
        (LANGUAGE_DELPHI, 'Delphi'),
        (LANGUAGE_RUBY, 'Ruby'),
        (LANGUAGE_CSHARP, 'C#'),
        (LANGUAGE_HASKELL, 'Haskell'),
        (LANGUAGE_OCAML, 'OCaml'),
        (LANGUAGE_SCALA, 'Scala'),
        (LANGUAGE_D, 'D'),
        (LANGUAGE_GO, 'Go'),
        (LANGUAGE_JAVASCRIPT, 'JavaScript'),
        (LANGUAGE_KOTLIN, 'Kotlin'),
        (LANGUAGE_RUST, 'Rust'),
        (LANGUAGE_CLANG, 'Clang'),
        (LANGUAGE_NODEJS, 'Node.js'),
        (LANGUAGE_PERL, 'Perl'),
        (LANGUAGE_SCHEME, 'Scheme'),
        (LANGUAGE_PHP, 'PHP'),
    )

    RESULT_UNDEFINED = ''
    RESULT_ACCEPTED = 'ACCEPTED'
    RESULT_WRONG_ANSWER = 'WRONG_ANSWER'
    RESULT_TIME_LIMIT_EXCEED = 'TIME_LIMIT_EXCEED'
    RESULT_MEMORY_LIMIT_EXCEED = 'MEMORY_LIMIT_EXCEED'
    RESULT_RUNTIME_ERROR = 'RUNTIME_ERROR'
    RESULT_SEGMENT_FAULT = 'SEGMENT_FAULT'
    RESULT_COMPILATION_ERROR = 'COMPILATION_ERROR'
    RESULT_NON_ZERO_EXIT_CODE = 'NON_ZERO_EXIT_CODE'
    RESULT_OUTPUT_LIMIT_EXCEED = 'OUTPUT_LIMIT_EXCEED'
    RESULT_PRESENTATION_ERROR = 'PRESENTATION_ERROR'
    RESULT_FLOAT_POINT_ERROR = 'FLOAT_POINT_ERROR'
    RESULT_CHOICES = (
        (RESULT_UNDEFINED, ''),
        (RESULT_ACCEPTED, 'Accepted'),
        (RESULT_WRONG_ANSWER, 'Wrong Answer'),
        (RESULT_TIME_LIMIT_EXCEED, 'Time Limit Exceed'),
        (RESULT_MEMORY_LIMIT_EXCEED, 'Memory Limit Exceed'),
        (RESULT_RUNTIME_ERROR, 'Runtime Error'),
        (RESULT_SEGMENT_FAULT, 'Segment Fault'),
        (RESULT_COMPILATION_ERROR, 'Compilation Error'),
        (RESULT_NON_ZERO_EXIT_CODE, 'Non Zero Exit Code'),
        (RESULT_OUTPUT_LIMIT_EXCEED, 'Output Limit Exceed'),
        (RESULT_PRESENTATION_ERROR, 'Presentation Error'),
        (RESULT_FLOAT_POINT_ERROR, 'Float Point Error'),
    )

    def __init__(self, **kwargs):
        self.id = 0
        self.language_id = ''
        self.result = ''
        self.run_time = 0
        self.run_memory = 0
        self.submit_time = 0
        self.problem_id = ''
        self.code = ''
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
