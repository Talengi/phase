# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework import permissions

from documents.models import Document
from discussion.models import Note
from discussion.api.serializers import NoteSerializer


class DiscussionViewSet(viewsets.ModelViewSet):
    model = Note
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        document_key = self.kwargs['document_key']
        revision = self.kwargs['revision']
        return Note.objects \
            .filter(document__document_key=document_key) \
            .filter(revision=revision) \
            .order_by('-created_on')

    def pre_save(self, obj):
        document_key = self.kwargs['document_key']
        revision = self.kwargs['revision']
        obj.document = Document.objects.get(document_key=document_key)
        obj.revision = revision
        obj.author = self.request.user
