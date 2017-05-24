# -*- coding: utf8 -*-



import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from elasticsearch.exceptions import ConnectionError

from search.utils import delete_index


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info('Deleting index %s' % settings.ELASTIC_INDEX)

        try:
            delete_index()
        except ConnectionError:
            raise CommandError('Elasticsearch cannot be found')
