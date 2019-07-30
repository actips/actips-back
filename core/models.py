import json
import re

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models

from core.exceptions import AppErrors
from django_base.base_member.models import AbstractMember, AbstractOAuthEntry, HierarchicalModel, UserOwnedModel, \
    ContentType, DatedModel


class Member(AbstractMember):
    class Meta:
        verbose_name = '会员'
        verbose_name_plural = '会员'
        db_table = 'core_member'

    def __str__(self):
        return '{}:{}'.format(self.pk, self.nickname)

    def get_granted_oj_sites(self):
        return [s.id for s in OnlineJudgeSite.objects.filter(user_profiles__user=self.user)]


class OAuthEntry(AbstractOAuthEntry):
    member = models.ForeignKey(
        verbose_name='OAuth凭据',
        to='core.Member',
        related_name='oauth_entries',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = 'OAuth凭据'
        verbose_name_plural = 'OAuth凭据'
        db_table = 'core_oauth_entry'

    @staticmethod
    def from_ticket(ticket, app_id, is_code=False):
        """
        :param ticket:
        :param app_id:
        :param is_code: 使用腾讯返回的 code 而不是 ticket 获取参数
        :return:
        """
        try:
            from django.conf import settings
            from urllib.request import urlopen
            from django_base.base_media.models import Image
            api_root = settings.WECHAT_API_ROOT.rstrip('/')
            url = api_root + ('/sns_user/{}/{}/'.format(app_id, ticket)
                              if is_code else '/ticket/{}/'.format(ticket))
            resp = urlopen(url)
            body = resp.read()
            data = json.loads(body)
            open_id = data.get('openid')
            union_id = data.get('unionid')
            entry, created = OAuthEntry.objects.get_or_create(
                app=settings.WECHAT_APPID, openid=open_id,
                defaults=dict(unionid=union_id)
            )
            # 无论如何，都更新头像、昵称和数据
            entry.headimgurl = data.get('headimgurl')
            entry.name = data.get('nickname')
            entry.nickname = data.get('nickname')
            entry.data = body
            # if not entry.avatar or entry.avatar.url() != data.get('avatar'):
            #     entry.avatar = Image.objects.create(ext_url=data.get('avatar'))
            entry.save()
            return entry
        except Exception as e:
            import traceback
            traceback.print_stack(e)
            # 微信票据失效
            raise AppErrors.ERROR_WECHAT_TICKET_INVALID

    def ensure_member(self):
        if not self.member:
            # 自动挂入用户
            from django.contrib.auth.hashers import make_password
            user, created = User.objects.get_or_create(
                username=self.openid,
                defaults=dict(password=make_password(None)),
            )
            self.member = Member.objects.create(user=user, nickname=self.nickname)
            self.save()
        return self.member


class OnlineJudgeSite(models.Model):
    name = models.CharField(
        verbose_name='站点名称',
        max_length=100,
    )

    code = models.CharField(
        verbose_name='简写代码',
        max_length=20,
    )

    charset = models.CharField(
        verbose_name='网站编码',
        max_length=20,
        default='utf8',
    )

    homepage = models.CharField(
        verbose_name='首页',
        max_length=255,
    )

    problem_url_template = models.CharField(
        verbose_name='问题链接',
        max_length=255,
        help_text='题目的网址链接，其中用{num}替代题目编号可以',
    )

    problem_fail_regex = models.CharField(
        verbose_name='抓取题目错误正则表达式',
        max_length=255,
        blank=True,
        default='',
        help_text='有些OJ没有找到题目也会返回200响应，这个时候需要用正则辅助判断是否找不到题目',
    )

    problem_title_regex = models.CharField(
        verbose_name='标题提取正则表达式',
        max_length=255,
        help_text='正则表达式字符串，提取第一个匹配组作为标题',
    )

    problem_content_css_selector = models.CharField(
        verbose_name='内容提取 css 选择器',
        max_length=255,
        blank=True,
        default='',
        help_text='通过抓取题目的网页 html 内容提取题目正文的 css 选择器',
    )

    # supported_languages = models.CharField(
    #     verbose_name='支持语言',
    #     max_length=255,
    #     help_text='指定该题目支持提交的语言，取值为OJ内部的提交语言编号，用 | 分割',
    #     blank=True,
    #     default='',
    # )

    class Meta:
        verbose_name = 'OJ站点'
        verbose_name_plural = 'OJ站点'
        db_table = 'core_online_judge_site'

    def __str__(self):
        return '[{}] {}'.format(self.code, self.name)

    # def save(self, *args, **kwargs):
    #     if 'get_supported_languages' in self.get_supported_features():
    #         self.supported_languages = '|'.join(self.get_adapter().get_supported_languages().map(lambda d: str(d.get('id'))))
    #     super().save(*args, **kwargs)

    def is_supported(self):
        from ojadapter.adapter import ALL_ADAPTERS
        return self.code in ALL_ADAPTERS

    def get_supported_features(self):
        features = []
        adapter = self.get_adapter()
        if adapter:
            for key, func in adapter.__class__.__dict__.items():
                from types import FunctionType
                from ojadapter.adapter import OJAdapterBase
                if type(func) == FunctionType and hasattr(OJAdapterBase, key) and \
                        func != getattr(OJAdapterBase, key):
                    features.append(key)
        return features

    def get_adapter(self):
        from ojadapter.adapter import ALL_ADAPTERS
        return ALL_ADAPTERS.get(self.code)

    def ping_problem(self, num, force_reload=False):
        # 如果有写适配器插件，调用专用的 download 方法
        adapter = self.get_adapter()
        if adapter:
            # TODO: 赛事指定题目尚未支持
            return self.download_problem(num, contest_id='', force_reload=force_reload)
        # 使用现存的题目
        problem = OnlineJudgeProblem.objects.filter(site=self, num=num).first()
        if problem and not force_reload:
            return problem
        # 重新抓取
        from urllib.request import urlopen
        url = self.problem_url_template.format(num=num)
        resp = urlopen(url)
        body = resp.read().decode(self.charset)
        # 判断返回的网页是否一个合法的题目
        pattern = re.compile(self.problem_fail_regex, re.MULTILINE)
        if self.problem_fail_regex and pattern.search(body):
            raise AppErrors.ERROR_FETCH_PROBLEM_FAIL_REGEX_MATCHED
        # 抓取标题
        pattern = re.compile(self.problem_title_regex, re.MULTILINE)
        result = pattern.findall(body)
        # print(body)
        if not result:
            raise AppErrors.ERROR_FETCH_PROBLEM_TITLE_NOT_MATCH
        title = result[0]
        # 解析题目正文内容
        if self.problem_content_css_selector:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(body, 'lxml')
            result = soup.select(self.problem_content_css_selector)
            # print(self.problem_content_css_selector)
            # print(result)
            if result:
                body = result[0]

        # 写入题目
        problem, created = OnlineJudgeProblem.objects.get_or_create(
            site=self, num=num, defaults=dict(
                title=title, content=body
            )
        )
        if not created:
            problem.title = title
            problem.content = body
            problem.save()
        return problem

    def download_problem(self, num, contest_id='', force_reload=False):
        # 缓存检测
        p, created = self.problems.get_or_create(
            num=num,
            contest_num=contest_id or '',
        )
        if not force_reload and not created and p.is_synced:
            return p
        # 下载
        adapter = self.get_adapter()
        problem = adapter.download_problem(num, contest_id)
        # 写入数据
        p.is_synced = True
        p.title = problem.title
        p.time_limit = problem.time_limit
        p.memory_limit = problem.memory_limit
        p.is_special_judge = problem.is_special_judge
        p.description = problem.description
        p.extra_description = problem.extra_description
        p.input_specification = problem.input_specification
        p.output_specification = problem.output_specification
        p.input_samples = '<!--DATA-SEPARATOR-->'.join(problem.input_samples)
        p.output_samples = '<!--DATA-SEPARATOR-->'.join(problem.output_samples)
        p.extra_info = problem.extra_info
        p.save()
        return p

    def grant_password(self, user, username, password, grant_store=False):
        """ 授权用户连接到当前OJ站点，使用用户名和密码登录，生成并保存OJ用户档案，
        如果允许保存密码，同时记录用户的密码。
        :param user:
        :param username:
        :param password:
        :param grant_store:
        :return:
        """
        # 首先尝试登录进去先
        adapter = self.get_adapter()
        if not adapter:
            raise AppErrors.ERROR_OJ_ADAPTER_REQUIRED
        ctx = adapter.get_user_context_by_user_and_password(username, password)
        ctx.save()
        if not adapter.check_context_validity(ctx):
            raise AppErrors.ERROR_OJ_CONTEXT_INVALID
        # 创建OJ用户档案
        profile, created = self.user_profiles.get_or_create(user=user)
        if grant_store:
            profile.username = username
            profile.password = password
        profile.session_info = ctx.context_id
        profile.save()
        # 授权之后要将用户在OJ上面的记录抓取放入任务队列
        from ojtasks.tasks import pull_user_submissions_oj
        pull_user_submissions_oj.delay(self.code, user.pk)
        return profile

    def is_granted_by(self, user):
        return self.user_profiles.filter(user=user).exists()

    def is_granted_by_current_user(self):
        from django_base.base_utils.middleware import get_request
        request = get_request()
        if not request or not hasattr(request.user, 'member'):
            return False
        return self.is_granted_by(request.user)

    def problem_count(self):
        return self.problems.filter(is_synced=True).count()

    def post_count(self):
        return ProblemPost.objects.filter(problem__site=self).count()

    def get_supported_languages(self):
        if 'get_supported_languages' not in self.get_supported_features():
            return []
        return self.get_adapter().get_supported_languages()


class OnlineJudgeUserProfile(DatedModel):
    site = models.ForeignKey(
        verbose_name='OJ站点',
        to='OnlineJudgeSite',
        related_name='user_profiles',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='用户',
        to='auth.User',
        related_name='online_judge_profiles',
        on_delete=models.CASCADE,
    )
    username = models.CharField(
        verbose_name='用户名',
        max_length=255,
        blank=True,
        default='',
    )
    password = models.CharField(
        verbose_name='密码',
        max_length=255,
        blank=True,
        default='',
    )
    session_info = models.TextField(
        verbose_name='会话信息',
        blank=True,
        default='',
    )

    class Meta:
        verbose_name = 'OJ用户档案'
        verbose_name_plural = 'OJ用户档案'
        db_table = 'core_online_judge_user_profile'
        unique_together = ['site', 'user']

    def get_context(self):
        from ojadapter.entity.UserContext import UserContext
        return UserContext(self.session_info)

    def validate(self):
        adapter = self.site.get_adapter()
        if not adapter:
            raise AppErrors.ERROR_OJ_ADAPTER_REQUIRED
        ctx = self.get_context()
        if not adapter.check_context_validity(ctx):
            raise AppErrors.ERROR_OJ_CONTEXT_INVALID

    def download_submissions(self):
        # 下载
        adapter = self.site.get_adapter()
        ctx = self.get_context()
        submissions = adapter.get_user_submission_list(ctx)
        for submission in submissions:
            OnlineJudgeSubmission.make(submission, self.site, self.user)


class OnlineJudgeProblem(models.Model):
    site = models.ForeignKey(
        verbose_name='站点',
        to='OnlineJudgeSite',
        related_name='problems',
        on_delete=models.PROTECT,
    )

    num = models.CharField(
        verbose_name='题目编号',
        max_length=50,
    )

    contest_num = models.CharField(
        verbose_name='题目编号',
        max_length=50,
        blank=True,
        default='',
    )

    title = models.CharField(
        verbose_name='标题',
        blank=True,
        max_length=255,
    )

    content = models.TextField(
        verbose_name='题目内容',
        blank=True,
        help_text='直接截取整个题目页面的HTML内容',
    )

    supported_languages = models.CharField(
        verbose_name='支持语言',
        max_length=255,
        help_text='指定该题目支持提交的语言，用 | 分割，如果没有填写，则为继承 OJ 的语言列表',
        blank=True,
        default='',
    )

    time_limit = models.IntegerField(
        verbose_name='时间限制',
        help_text='时间限制，单位为毫秒',
        default=0,
    )

    memory_limit = models.IntegerField(
        verbose_name='内存限制',
        help_text='内存限制，单位为KB',
        default=0,
    )

    is_special_judge = models.BooleanField(
        verbose_name='是否SpecialJudge',
        default=False,
    )

    description = models.TextField(
        verbose_name='题目描述',
        blank=True,
        default='',
        help_text='题目描述部分，格式为Markdown'
    )

    extra_description = models.TextField(
        verbose_name='额外题目描述',
        blank=True,
        default='',
        help_text='题目描述部分，格式为Markdown'
    )

    input_specification = models.TextField(
        verbose_name='输入描述',
        blank=True,
        default='',
        help_text='题目输入描述'
    )

    output_specification = models.TextField(
        verbose_name='输出描述',
        blank=True,
        default='',
        help_text='题目输出描述'
    )

    input_samples = models.TextField(
        verbose_name='样例输入',
        blank=True,
        default='',
        help_text='题目输出描述'
    )

    output_samples = models.TextField(
        verbose_name='样例输出',
        blank=True,
        default='',
        help_text='题目输出描述'
    )

    extra_info = models.TextField(
        verbose_name='额外信息',
        blank=True,
        help_text='一些不好定位的附加信息，用 JSON 传入',
    )

    is_synced = models.BooleanField(
        verbose_name='是否同步',
        default=False,
    )

    class Meta:
        verbose_name = 'OJ问题'
        verbose_name_plural = 'OJ问题'
        db_table = 'core_online_judge_problem'
        unique_together = (('site', 'num'),)

    def code(self):
        return '{}{}'.format(self.site.code, self.num)

    def online_judge_url(self):
        return self.site.problem_url_template.format(num=self.num)

    def get_extra_info(self, key='', default=None):
        extra_info = json.loads(self.extra_info or '{}')
        if not key:
            return extra_info
        return extra_info.get(key, default)

    def get_supported_languages(self):
        if 'get_supported_languages' not in self.site.get_supported_features():
            return []
        adapter = self.site.get_adapter()
        all_languages = adapter.get_supported_languages()
        # 题目无指定的话就支持 OJ 所有的语言
        if not self.supported_languages:
            return all_languages
        # 题目有指定的话，按照 | 分割的 id 值筛选所有的 OJ 语言
        ids = self.supported_languages.split('|')
        return list(filter(lambda d: str(d.get('id')) in ids, all_languages))

    def submit(self, user, language_id, code, use_platform_account=False):
        adapter = self.site.get_adapter()
        if not adapter:
            raise AppErrors.ERROR_OJ_ADAPTER_REQUIRED
        if 'submit_problem' not in self.site.get_supported_features():
            raise AppErrors.ERROR_PASSWORD_TOO_SIMPLE
        from ojtasks.tasks import submit_online_judge_problem
        submit_online_judge_problem.delay(
            self.id, user.id, language_id, code, use_platform_account=use_platform_account
        )


class OnlineJudgeSubmission(UserOwnedModel):
    from ojadapter.entity.Submission import Submission
    problem = models.ForeignKey(
        verbose_name='题目',
        to='OnlineJudgeProblem',
        related_name='submissions',
        on_delete=models.CASCADE,
    )

    submission_id = models.IntegerField(
        verbose_name='OJ提交编号',
        default=0,
    )

    language = models.CharField(
        verbose_name='语言',
        max_length=30,
        choices=Submission.LANGUAGE_CHOICES,
    )

    language_id = models.CharField(
        verbose_name='语言ID',
        max_length=30,
        blank=True,
        help_text='OJ的内部语言编号',
    )

    code = models.TextField(
        verbose_name='代码',
        blank=True,
        default='',
    )

    result = models.CharField(
        verbose_name='结果',
        max_length=30,
        choices=Submission.RESULT_CHOICES,
        blank=True,
        default='',
    )

    run_time = models.IntegerField(
        verbose_name='运行时间',
        default=0,
    )

    run_memory = models.IntegerField(
        verbose_name='运行内存',
        default=0,
    )

    submit_time = models.DateTimeField(
        verbose_name='提交时间',
    )

    class Meta:
        verbose_name = '提交记录'
        verbose_name_plural = '提交记录'
        db_table = 'core_online_judge_submission'

    @staticmethod
    def make(submission, site, user):
        """ 根据 OJAdapter 获取回来的 Submission 对象构造一个提交记录并分配给制定的用户
        :param submission:
        :param site:
        :param user:
        :return:
        """
        problem = site.problems.filter(num=submission.problem_id).first()
        if not problem:
            return None
        adapter = site.get_adapter()
        language = adapter.get_language_by_id(submission.language_id)
        s, created = user.onlinejudgesubmissions_owned.get_or_create(
            problem=problem,
            submission_id=submission.id,
            language=language.get('language'),
            language_id=language.get('id'),
            submit_time=submission.submit_time,
            defaults=dict()
        )
        s.result = submission.result
        s.run_time = submission.run_time
        s.run_memory = submission.run_memory
        s.code = submission.code
        s.save()
        return s


class ProblemCategory(HierarchicalModel):
    name = models.CharField(
        verbose_name='分类名称',
        max_length=100,
        unique=True,
    )

    seq = models.CharField(
        verbose_name='序号',
        max_length=20,
        blank=True,
        default=True,
    )

    class Meta:
        verbose_name = '问题分类'
        verbose_name_plural = '问题分类'
        db_table = 'problem_category'

    def __str__(self):
        return self.name

    def calculate(self):
        """ 计算所有计算列
        :return:
        """
        # 计算排序编号
        self.seq = '{:04d}'.format(self.id)
        if self.parent:
            self.parent.calculate()
            self.seq = self.parent.seq + self.seq
        self.save()


class ProblemPost(UserOwnedModel):
    title = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )

    content = models.TextField(
        verbose_name='正文内容',
        blank=True,
        default='',
    )

    problem = models.ForeignKey(
        verbose_name='对应题目',
        to='OnlineJudgeProblem',
        related_name='posts',
        on_delete=models.PROTECT,
    )

    problems_related = models.ManyToManyField(
        verbose_name='关联题目',
        blank=True,
        to='OnlineJudgeProblem',
        related_name='posts_related'
    )

    origin_link = models.CharField(
        verbose_name='原文链接',
        help_text='留空的话视作原创',
        max_length=250,
        blank=True,
        null=True,
        unique=True,  # 为了排除多余的文章导入，有必要通过原文链接排重
    )

    categories = models.ManyToManyField(
        verbose_name='标记分类',
        to='ProblemCategory',
        related_name='posts',
    )

    # TODO: 如果一个用户对题目的评级在统计意义上与平均值相比，明显偏高或者偏低，这个指标可以用来指示用户对自己水平的主观评价
    rating_difficulty = models.IntegerField(
        verbose_name='难度评级',
        default=0,
        help_text='1-5，最难为5，最容易为1，0的话是尚未评分'
    )

    comments = GenericRelation(
        verbose_name='评论',
        to='Comment',
        related_name='problem_posts',
    )

    date_created = models.DateTimeField(
        verbose_name='创建时间',
        auto_now_add=True,
    )

    date_updated = models.DateTimeField(
        verbose_name='修改时间',
        auto_now=True,
    )

    class Meta:
        verbose_name = '题解'
        verbose_name_plural = '题解'
        db_table = 'core_problem_post'

    def save(self, *args, **kwargs):
        # 必须显式原创声明或者指定原文链接
        if self.origin_link == '':
            raise AppErrors.ERROR_POST_REQUIRE_ORIGIN_LINK
        super().save(*args, **kwargs)


class UserLog(UserOwnedModel):
    date_created = models.DateTimeField(
        verbose_name='时间',
        auto_now_add=True,
    )

    action = models.CharField(
        verbose_name='动作',
        max_length=20,
    )

    remark = models.CharField(
        verbose_name='备注',
        max_length=45,
        blank=True,
        default='',
    )

    class Meta:
        verbose_name = '用户日志'
        verbose_name_plural = '用户日志'
        db_table = 'core_user_log'


class Comment(UserOwnedModel,
              HierarchicalModel):
    content = models.TextField(
        verbose_name='评论内容',
    )

    content_type = models.ForeignKey(
        verbose_name='关联类型',
        to='contenttypes.ContentType',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey()

    date_created = models.DateTimeField(
        verbose_name='评论时间',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = '用户评论'
        verbose_name_plural = '用户评论'
        db_table = 'core_comment'
