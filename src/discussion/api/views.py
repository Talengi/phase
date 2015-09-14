# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework import permissions

from documents.models import Document
from reviews.models import Review
from discussion.models import Note
from discussion.api.serializers import NoteSerializer


class DiscussionPermission(permissions.BasePermission):
    """Custom discussion permission.

      * All the category members can access the discussion.
      * All distribution list members can post a new messages
      * Only the author of a message can update or delete it.

    """

    def has_permission(self, request, view):
        """Is the user a member of the distribution list?."""

        # Read only method, allow all category members
        if request.method in permissions.SAFE_METHODS:
            authorized = request.user in view.document.category.users.all()

        # Write methods, only distribution list members
        else:
            reviews = Review.objects \
                .filter(document__document_key=view.document_key) \
                .filter(reviewer=request.user) \
                .filter(revision=view.revision)
            authorized = (reviews.count() > 0)

        return authorized

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class DiscussionViewSet(viewsets.ModelViewSet):
    model = Note
    serializer_class = NoteSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        DiscussionPermission
    )

    def dispatch(self, request, *args, **kwargs):
        self.document_key = kwargs['document_key']
        self.revision = kwargs['revision']
        self.document = Document.objects \
            .select_related('category__organisation', 'category__category_template') \
            .get(document_key=self.document_key)
        return super(DiscussionViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Note.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .order_by('created_on')

    def perform_create(self, serializer):
        serializer.save(
            document=self.document,
            revision=self.revision,
            author=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()
        instance.save()
