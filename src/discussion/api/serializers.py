# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template import defaultfilters as filters
from rest_framework import serializers

from discussion.models import Note


class NoteSerializer(serializers.ModelSerializer):
    document = serializers.Field()
    author = serializers.Field(source='author_id')
    author_email = serializers.Field(source='author.email')
    created_on = serializers.DateTimeField(read_only=True)
    formatted_created_on = serializers.DateTimeField(read_only=True, source='created_on')
    formatted_body = serializers.Field(source='body')

    class Meta:
        model = Note

    def transform_formatted_created_on(self, obj, value):
        formatted = filters.date(value, 'SHORT_DATETIME_FORMAT')
        return formatted

    def transform_formatted_body(self, obj, value):
        formatted = filters.linebreaksbr(value)
        return formatted
