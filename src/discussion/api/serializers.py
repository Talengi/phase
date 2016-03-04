# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template import defaultfilters as filters
from rest_framework import serializers

from discussion.models import Note, mentions_re


class NoteSerializer(serializers.ModelSerializer):
    document_id = serializers.ReadOnlyField(source='document.id')
    revision = serializers.ReadOnlyField()
    author_id = serializers.ReadOnlyField(source='author.id')
    author_email = serializers.ReadOnlyField(source='author.email')
    created_on = serializers.DateTimeField(read_only=True)
    formatted_created_on = serializers.DateTimeField(
        read_only=True,
        source='created_on',
        format=None)
    formatted_body = serializers.ReadOnlyField(source='body')
    is_deleted = serializers.ReadOnlyField(source='deleted_on')

    class Meta:
        model = Note
        fields = ('id', 'document_id', 'revision', 'author_id', 'author_email',
                  'body', 'formatted_body', 'created_on',
                  'formatted_created_on', 'is_deleted')

    def to_representation(self, instance):
        ret = super(NoteSerializer, self).to_representation(instance)
        ret['formatted_created_on'] = filters.date(
            ret['formatted_created_on'],
            'SHORT_DATETIME_FORMAT')

        ret['is_deleted'] = bool(ret['is_deleted'])

        formatted = ret['formatted_body']
        replace = r'<span class="mention">@\1</span>'
        formatted = mentions_re.sub(replace, formatted)
        formatted = filters.safe(formatted)
        formatted = filters.linebreaksbr(formatted)
        formatted = filters.urlize(formatted)
        ret['formatted_body'] = formatted
        return ret
