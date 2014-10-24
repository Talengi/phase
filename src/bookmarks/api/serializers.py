# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from bookmarks.models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    user = serializers.Field(source='user.email')

    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'name', 'url')
