# -*- coding: utf-8 -*-


from rest_framework import serializers

from accounts.models import User
from distriblists.models import DistributionList


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name')


class DistributionListSerializer(serializers.ModelSerializer):
    leader = UserSerializer()
    approver = UserSerializer()
    reviewers = UserSerializer(many=True)

    class Meta:
        model = DistributionList
        fields = ('id', 'name', 'leader', 'approver', 'reviewers')
