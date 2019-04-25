from django.conf import settings
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import core.models as m
from core.exceptions import AppErrors
from django_base.base_utils.app_error.utils import validate_params
from . import serializers as s
from django_base.base_utils import utils as u


class MemberViewSet(viewsets.GenericViewSet):
    # search_fields = ['name']
    queryset = m.Member.objects.filter(user__is_active=True)
    serializer_class = s.MemberSerializer
    filter_fields = '__all__'
    ordering = ['-pk']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    @action(methods=['POST'], detail=False)
    def login_with_ticket(self, request):
        # 获取 OAuth 凭据
        ticket = request.data.get('ticket')
        entry = m.OAuthEntry.from_ticket(ticket, settings.WECHAT_APPID)

        # 获取登录的用户（自动注册）
        member = entry.ensure_member()
        if not member.user.is_active:
            raise AppErrors.ERROR_USER_INACTIVE
        # 实施登陆
        from django.contrib.auth import login
        login(request, member.user)
        return u.response_success('登录成功')

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        from django.contrib.auth import logout
        logout(request)
        return u.response_success('登录成功')

    @action(methods=['GET'], detail=False)
    def current(self, request):
        # 尚未登录
        if request.user.is_anonymous:
            raise AppErrors.ERROR_NOT_SIGN_IN
        member = self.get_queryset().filter(user=request.user).first()
        if not member:
            raise AppErrors.ERROR_MEMBER_INEXISTS
        return Response(data=s.MemberSerializer(member).data)
