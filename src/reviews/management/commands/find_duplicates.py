# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.db.models import Count

from documents.models import Document
from reviews.models import Review


class Command(BaseCommand):
    def handle(self, *args, **options):
        reviews = Review.objects \
            .values('reviewer', 'document', 'revision') \
            .annotate(Count('id')) \
            .order_by() \
            .filter(id__count__gt=1)

        document_ids = [review['document'] for review in reviews]
        unique_ids = set(document_ids)
        documents = Document.objects.filter(id__in=unique_ids)

        for doc in documents:
            self.stdout.write('Found duplicate in {.document_key}'.format(doc))
