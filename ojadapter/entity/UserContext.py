import pickle

import requests
import os
import os.path
from uuid import uuid4

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class UserContext(object):

    def __init__(self, context_id=''):
        self.context_id = context_id or str(uuid4())
        self.session_file_path = os.path.join(BASE_DIR, '.session', self.context_id)
        if not os.path.isdir(os.path.dirname(self.session_file_path)):
            os.makedirs(os.path.dirname(self.session_file_path), exist_ok=True)

        if os.path.isfile(self.session_file_path):
            self.session = pickle.load(open(self.session_file_path, 'rb'))
        else:
            self.session = requests.Session()

    def save(self):
        file = open(self.session_file_path, 'wb')
        pickle.dump(self.session, file)
        file.close()

    def delete(self):
        if os.path.isfile(self.session_file_path):
            os.remove(self.session_file_path)

    def print(self):
        [print('>>>>', k, '>>>>\n' + str(v), '\n<<<<\n') for k, v in self.__dict__.items()]
