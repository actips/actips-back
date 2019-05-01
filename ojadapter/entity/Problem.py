class Problem(object):

    def __init__(self):
        self.id = 0
        self.contest_id = 0
        # 标题
        self.title = ''
        # 时间限制（整数/秒）
        self.time_limit = 0
        # 内存限制（整数/KB）
        self.memory_limit = 0
        self.is_special_judge = False
        self.description = ''
        self.extra_description = ''
        self.input_specification = ''
        self.output_specification = ''
        self.input_samples = []
        self.output_samples = []
        self.author = ''
        self.source = ''

    def print(self):
        [print('>>>>', k, '>>>>\n' + str(v), '\n<<<<\n') for k, v in self.__dict__.items()]

