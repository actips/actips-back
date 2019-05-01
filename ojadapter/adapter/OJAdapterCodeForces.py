from ..utils import request_dom
from .OJAdapterBase import OJAdapterBase
from urllib.request import urlopen


class OJAdapterCodeForces(OJAdapterBase):
    code = 'CF'
    homepage = r'http://codeforces.com'

    def get_supported_languages(self):
        return 1

    def get_all_content_numbers(self):
        # 获取种子页
        soup = request_dom(r'{}/problemset'.format(self.homepage))
        result = soup.select('.pagination ul li span.page-index')
        print(result)

    def test_01_get_all_content_numbers(self):
        self.get_all_content_numbers()
