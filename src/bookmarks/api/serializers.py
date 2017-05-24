from rest_framework import serializers

from bookmarks.models import Bookmark
from categories.models import Category


class BookmarkSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Bookmark
        fields = ('id', 'category', 'name', 'url')
