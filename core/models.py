import json
import re

from django.contrib.auth.models import User
from django.db import models

from core.exceptions import AppErrors
from django_base.base_member.models import AbstractMember, AbstractOAuthEntry, HierarchicalModel, UserOwnedModel


class Member(AbstractMember):
    class Meta:
        verbose_name = '会员'
        verbose_name_plural = '会员'
        db_table = 'core_member'

    def __str__(self):
        return '{}:{}'.format(self.pk, self.nickname)


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

    class Meta:
        verbose_name = 'OJ站点'
        verbose_name_plural = 'OJ站点'
        db_table = 'core_online_judge_site'

    def __str__(self):
        return '[{}] {}'.format(self.code, self.name)

    def ping_problem(self, num, force_reload=False):
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

    title = models.CharField(
        verbose_name='标题',
        max_length=255,
    )

    content = models.TextField(
        verbose_name='题目内容',
        help_text='直接截取整个题目页面的HTML内容',
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


class ProblemCategory(HierarchicalModel):
    name = models.CharField(
        verbose_name='分类名称',
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = '问题分类'
        verbose_name_plural = '问题分类'
        db_table = 'problem_category'

    def __str__(self):
        return self.name


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
