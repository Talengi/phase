# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import generics

from documents.models import Document
from restapi.views import CategoryAPIViewMixin
from ..models import Activity
from .serializers import ActivitySerializer


class AuditTrailList(CategoryAPIViewMixin, generics.ListAPIView):
    model = Activity
    serializer_class = ActivitySerializer

    def get_queryset(self):
        ct = ContentType.objects.get_for_model(Document)
        document_key = self.kwargs.get('document_key')
        document = Document.objects.get(
            category=self.get_category(), document_key=document_key)
        revision_class = document.category.revision_class()
        rev_ct = ContentType.objects.get_for_model(revision_class)
        revisions_pk = document.get_all_revisions().values_list('pk', flat=True)

        qs = Activity.objects.filter(
            Q(action_object_content_type=ct, action_object_object_id=document.pk) |
            Q(target_content_type=ct, target_object_id=document.pk) |
            Q(action_object_content_type=rev_ct, action_object_object_id__in=revisions_pk) |
            Q(target_content_type=rev_ct, target_object_id__in=revisions_pk))
        return qs
