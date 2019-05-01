from django.test import TestCase, SimpleTestCase
from .. import adapter


class TestCaseAdapters(SimpleTestCase):

    def test_all(self):
        for name, cls in adapter.__dict__.items():
            if not name.startswith('OJAdapter') or name == 'OJAdapterBase':
                continue
            adt = cls()
            for key in dir(adt):
                method = getattr(adt, key)
                if key.startswith('test') and callable(method):
                    print('Testing {}.{}'.format(name, key))
                    method()
