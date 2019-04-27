from django.conf import settings
from django.db import models
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

import core.models as m
from core.exceptions import AppErrors
from django_base.base_media.models import Image
from django_base.base_utils import utils as u
from . import serializers as s


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


class OnlineJudgeSiteViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    queryset = m.OnlineJudgeSite.objects.all()
    serializer_class = s.OnlineJudgeSiteSerializer
    filter_fields = '__all__'
    ordering = ['-pk']

    @action(methods=['POST'], detail=True)
    def ping_problem(self, request, pk):
        site = self.get_object()
        # TODO: 调试方便，总是强制重新抓取
        problem = site.ping_problem(request.data.get('num'), force_reload=True)
        if not problem:
            return u.response_fail('没有找到题目')
        return Response(data=s.OnlineJudgeProblemSerializer(problem).data)


class OnlineJudgeProblemViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    queryset = m.OnlineJudgeProblem.objects.all()
    serializer_class = s.OnlineJudgeProblemSerializer
    filter_fields = '__all__'
    ordering = ['-pk']


class ProblemPostViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = m.ProblemPost.objects.all()
    serializer_class = s.ProblemPostSerializer
    filter_fields = '__all__'
    ordering = ['-pk']
    search_fields = ['title', 'problems__title']
    allowed_deep_params = [
        'categories__id',
        'problems__site__id',
    ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        if request.user != item.author:
            raise AppErrors.ERROR_DELETE_NOT_PERMITTED
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        if request.user != item.author:
            raise AppErrors.ERROR_UPDATE_NOT_PERMITTED
        return super().update(request, *args, **kwargs)


class ProblemCategoryViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    queryset = m.ProblemCategory.objects.all()
    serializer_class = s.ProblemCategorySerializer
    filter_fields = '__all__'
    ordering = ['-pk']


class ImageViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = s.ImageSerializer
    filter_fields = '__all__'
    ordering = ['-pk']
