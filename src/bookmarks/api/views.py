# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework import permissions

from bookmarks.models import Bookmark
from bookmarks.api.serializers import BookmarkSerializer


class BookmarkViewSet(viewsets.ModelViewSet):
    model = Bookmark
    serializer_class = BookmarkSerializer
    paginate_by_param = 'page_limit'
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def pre_save(self, obj):
        obj.user = self.request.user
