# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from elasticsearch.exceptions import ConnectionError

from categories.models import Category
from search import elastic
from search.utils import get_mapping


class Command(BaseCommand):
    def handle(self, *args, **options):
        index = settings.ELASTIC_INDEX

        categories = Category.objects.select_related('category_template').all()
        for category in categories:
            doc_class = category.document_class()
            doc_type = category.document_type()

            self.stdout.write('Creating mapping for document type %s' % doc_class.__name__)
            mapping = get_mapping(doc_class)

            try:
                elastic.indices.put_mapping(
                    index=index,
                    doc_type=doc_type,
                    body=mapping
                )
            except ConnectionError:
                raise CommandError('Elasticsearch cannot be found')
