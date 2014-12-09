# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template import defaultfilters as filters
from rest_framework import serializers

from discussion.models import Note


class NoteSerializer(serializers.ModelSerializer):
    document = serializers.Field()
    author = serializers.Field(source='author.email')
    created_on = serializers.DateTimeField()
    formatted_created_on = serializers.DateTimeField(source='created_on')

    class Meta:
        model = Note
        fields = ('id', 'document', 'author', 'body', 'created_on',
                  'formatted_created_on')

    def transform_formatted_created_on(self, obj, value):
        formatted = filters.date(value, 'SHORT_DATETIME_FORMAT')
        return formatted
