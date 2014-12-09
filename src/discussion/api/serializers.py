# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from discussion.models import Note


class NoteSerializer(serializers.ModelSerializer):
    document = serializers.Field()
    author = serializers.Field(source='author.email')
    created_on = serializers.Field()

    class Meta:
        model = Note
        fields = ('id', 'document', 'author', 'body', 'created_on')
