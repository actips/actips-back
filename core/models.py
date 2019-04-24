from django.db import models

from django_base.base_member.models import AbstractMember, AbstractOAuthEntry


class Member(AbstractMember):
    class Meta:
        verbose_name = '会员'
        verbose_name_plural = '会员'
        db_table = 'core_member'


class OAuthEntry(AbstractOAuthEntry):
    class Meta:
        verbose_name = '会员'
        verbose_name_plural = '会员'
        db_table = 'core_oauth_entry'
