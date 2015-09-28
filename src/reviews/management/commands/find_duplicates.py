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

        for review in reviews:
            self.cancel_review(review['document'], review['revision'])

    def cancel_review(self, doc_id, revision_id):
        document = Document.objects.get(pk=doc_id)
        revision = document.get_metadata().get_revision(revision_id)

        self.stdout.write('Found duplicate in {.document_key}'.format(document))
        revision.cancel_review()
