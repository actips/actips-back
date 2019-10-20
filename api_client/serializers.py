from rest_framework import serializers, mixins

import core.models as m
from django_base.base_media.models import Image


class MemberSerializer(serializers.ModelSerializer):
    avatar_url = serializers.ReadOnlyField(source='oauth_entries.first.headimgurl')
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    granted_oj_sites = serializers.ReadOnlyField(source='get_granted_oj_sites')

    class Meta:
        model = m.Member
        fields = '__all__'


class OnlineJudgeSiteSerializer(serializers.ModelSerializer):
    is_supported = serializers.ReadOnlyField()
    supported_features = serializers.ReadOnlyField(source='get_supported_features')
    problem_count = serializers.ReadOnlyField()
    post_count = serializers.ReadOnlyField()
    is_granted = serializers.ReadOnlyField(source='is_granted_by_current_user')

    class Meta:
        model = m.OnlineJudgeSite
        fields = '__all__'


class OnlineJudgeProblemSerializer(serializers.ModelSerializer):
    site_code = serializers.ReadOnlyField(source='site.code')
    online_judge_url = serializers.ReadOnlyField()
    supported_languages = serializers.ReadOnlyField(source='get_supported_languages')
    submission_count = serializers.ReadOnlyField()
    submission_count_self = serializers.ReadOnlyField()
    submission_count_self_accepted = serializers.ReadOnlyField()

    class Meta:
        model = m.OnlineJudgeProblem
        fields = '__all__'


class OnlineJudgeSubmissionSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=m.User.objects.all(), required=False)
    problem_num = serializers.ReadOnlyField(source='problem.num')
    problem_title = serializers.ReadOnlyField(source='problem.title')

    class Meta:
        model = m.OnlineJudgeSubmission
        exclude = ['code']


class ProblemCategorySerializer(serializers.ModelSerializer):
    post_count = serializers.ReadOnlyField()

    class Meta:
        model = m.ProblemCategory
        fields = '__all__'


class ProblemPostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=m.User.objects.all(), required=False)
    problem_title = serializers.ReadOnlyField(
        source='problem.title')
    problem_site_code = serializers.ReadOnlyField(
        source='problem.site.code')
    problem_num = serializers.ReadOnlyField(
        source='problem.num')
    problem_url = serializers.ReadOnlyField()
    problems_related_item = OnlineJudgeProblemSerializer(
        source='problems_related', many=True, read_only=True)
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


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=m.User.objects.all(), required=False)
    author_nickname = serializers.ReadOnlyField(
        source='author.member.nickname')
    parent_nickname = serializers.ReadOnlyField(
        source='parent.author.member.nickname')

    class Meta:
        model = m.Comment
        fields = '__all__'
