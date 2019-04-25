from rest_framework import serializers

import core.models as m


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Member
        fields = '__all__'
