# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template import defaultfilters as filters
from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.Field(source='user.email')
    iso_formatted_created_on = serializers.DateTimeField(read_only=True, source='created_on')
    natural_formatted_created_on = serializers.DateTimeField(read_only=True, source='created_on')

    class Meta:
        model = Notification
        fields = ('id', 'user', 'body', 'created_on',
                  'iso_formatted_created_on', 'natural_formatted_created_on',
                  'seen')

    def transform_iso_formatted_created_on(self, obj, value):
        formatted = filters.date(value, 'c')
        return formatted

    def transform_natural_formatted_created_on(self, obj, value):
        formatted = naturaltime(value)
        return formatted
