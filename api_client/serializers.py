from rest_framework import serializers,mixins

import core.models as m


class MemberSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.ReadOnlyField(source='oauth_entries.first.headimgurl')

    class Meta:
        model = m.Member
        fields = '__all__'


class OnlineJudgeSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.OnlineJudgeSite
        fields = '__all__'


class OnlineJudgeProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.OnlineJudgeProblem
        fields = '__all__'


class ProblemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = m.ProblemCategory
        fields = '__all__'


class ProblemPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.ProblemPost
        fields = '__all__'
