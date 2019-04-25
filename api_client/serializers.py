from rest_framework import serializers

import core.models as m


class MemberSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.ReadOnlyField(source='oauth_entries.first.headimgurl')

    class Meta:
        model = m.Member
        fields = '__all__'
