# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from ..models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    created_on = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Activity
        fields = ('text', 'created_on')

    def get_text(self, obj):
        return str(obj)

