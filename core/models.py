import json

from django.contrib.auth.models import User
from django.db import models

from core.exceptions import AppErrors
from django_base.base_member.models import AbstractMember, AbstractOAuthEntry


class Member(AbstractMember):
    class Meta:
        verbose_name = '会员'
        verbose_name_plural = '会员'
        db_table = 'core_member'


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
        verbose_name = '会员'
        verbose_name_plural = '会员'
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
