# -*- coding: utf-8 -*-



from rest_framework import viewsets
from rest_framework import permissions

from bookmarks.models import Bookmark
from bookmarks.api.serializers import BookmarkSerializer


class BookmarkViewSet(viewsets.ModelViewSet):
    model = Bookmark
    serializer_class = BookmarkSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
