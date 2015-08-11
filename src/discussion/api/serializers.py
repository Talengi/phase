# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template import defaultfilters as filters
from rest_framework import serializers

from discussion.models import Note, mentions_re


class NoteSerializer(serializers.ModelSerializer):
    document = serializers.Field()
    revision = serializers.Field()
    author_id = serializers.Field(source='author_id')
    author_email = serializers.Field(source='author.email')
    created_on = serializers.DateTimeField(read_only=True)
    formatted_created_on = serializers.DateTimeField(read_only=True, source='created_on')
    formatted_body = serializers.Field(source='body')

    class Meta:
        model = Note
        fields = ('id', 'document', 'revision', 'author_id', 'author_email',
                  'body', 'formatted_body', 'created_on',
                  'formatted_created_on')

    def to_representation(self, instance):
        ret = super(NoteSerializer, self).to_representation(instance)
        ret['formatted_created_on'] = filters.date(
            ret['formatted_created_on'],
            'SHORT_DATETIME_FORMAT')

        formatted = ret['formatted_body']
        replace = r'<span class="mention">@\1</span>'
        formatted = mentions_re.sub(replace, formatted)
        formatted = filters.linebreaksbr(formatted)
        ret['formatted_body'] = formatted

        return ret
