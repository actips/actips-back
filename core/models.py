import json

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
            user, created = User.objects.get_or_create(
                username=self.openid,
                defaults=dict(password=None),
            )
            self.member = Member.objects.create(user=user, nickname=self.nickname)
            self.save()
        return self.member


class OnlineJudgeSite(models.Model):
    name = models.CharField(
        verbose_name='站点名称',
        max_length=100,
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

    problem_title_regex = models.CharField(
        verbose_name='标题提取正则表达式',
        max_length=255,
        help_text='正则表达式字符串，提取第一个匹配组作为标题',
    )

    class Meta:
        verbose_name = 'OJ站点'
        verbose_name_plural = 'OJ站点'
        db_table = 'online_judge_site'

    def ping_problem(self):
        pass


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
        db_table = 'online_judge_problem'
        unique_together = (('site', 'num'),)


class ProblemCategory(HierarchicalModel):
    name = models.CharField(
        verbose_name='分类名称',
        max_length=100,
    )

    class Meta:
        verbose_name = '问题分类'
        verbose_name_plural = '问题分类'
        db_table = 'problem_category'


class ProblemPost(UserOwnedModel):
    title = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )

    excerpt = models.TextField(
        verbose_name='摘要',
    )

    content = models.TextField(
        verbose_name='正文内容',
        blank=True,
        default='',
    )

    problems = models.ManyToManyField(
        verbose_name='相关题目',
        to='OnlineJudgeProblem',
        related_name='posts',
    )

    categories = models.ManyToManyField(
        verbose_name='标记分类',
        to='ProblemCategory',
        related_name='posts',
    )

    class Meta:
        verbose_name = '题解'
        verbose_name_plural = '题解'
        db_table = 'core_problem_post'
