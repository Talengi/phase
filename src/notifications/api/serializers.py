# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template import defaultfilters as filters
from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    iso_formatted_created_on = serializers.DateTimeField(read_only=True, source='created_on')
    natural_formatted_created_on = serializers.DateTimeField(read_only=True, source='created_on')

    class Meta:
        model = Notification
        fields = ('id', 'body', 'created_on', 'iso_formatted_created_on',
                  'natural_formatted_created_on', 'seen')

    def to_representation(self, instance):
        ret = super(NotificationSerializer, self).to_representation(instance)

        ret['iso_formatted_created_on'] = filters.date(
            ret['iso_formatted_created_on'], 'c')

        ret['natural_formatted_created_on'] = naturaltime(
            ret['natural_formatted_created_on'])

        return ret
