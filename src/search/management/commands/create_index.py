# -*- coding: utf8 -*-



import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from elasticsearch.exceptions import ConnectionError

from search.utils import create_index


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info('Creating index %s' % settings.ELASTIC_INDEX)

        try:
            create_index()
        except ConnectionError:
            raise CommandError('Elasticsearch cannot be found')
