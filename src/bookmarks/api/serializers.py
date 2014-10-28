# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from bookmarks.models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Bookmark
        fields = ('id', 'category', 'name', 'url')
