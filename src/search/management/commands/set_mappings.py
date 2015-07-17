# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging

from django.core.management.base import BaseCommand, CommandError

from elasticsearch.exceptions import ConnectionError

from categories.models import Category
from search.utils import put_category_mapping


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        categories = Category.objects \
            .select_related('category_template__metadata_model')
        for category in categories:
            doc_class = category.document_class()
            logger.info('Creating mapping for document type %s' % doc_class.__name__)
            try:
                put_category_mapping(category.id)
            except ConnectionError:
                raise CommandError('Elasticsearch cannot be found')
