from rest_framework import serializers, mixins

import core.models as m
from django_base.base_media.models import Image


class MemberSerializer(serializers.ModelSerializer):
    avatar_url = serializers.ReadOnlyField(source='oauth_entries.first.headimgurl')

    class Meta:
        model = m.Member
        fields = '__all__'


class OnlineJudgeSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.OnlineJudgeSite
        fields = '__all__'


class OnlineJudgeProblemSerializer(serializers.ModelSerializer):
    site_code = serializers.ReadOnlyField(source='site.code')
    online_judge_url = serializers.ReadOnlyField()

    class Meta:
        model = m.OnlineJudgeProblem
        fields = '__all__'


class ProblemCategorySerializer(serializers.ModelSerializer):
    post_count = serializers.ReadOnlyField()

    class Meta:
        model = m.ProblemCategory
        fields = '__all__'


class ProblemPostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=True)
    problems_item = OnlineJudgeProblemSerializer(
        source='problems', many=True, read_only=True)
    categories_item = ProblemCategorySerializer(
        source='categories', many=True, read_only=True)
    author_avatar_url = serializers.ReadOnlyField(
        source='author.member.oauth_entries.first.headimgurl')
    author_nickname = serializers.ReadOnlyField(
        source='author.member.nickname')

    class Meta:
        model = m.ProblemPost
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField()

    class Meta:
        model = Image
        fields = '__all__'
