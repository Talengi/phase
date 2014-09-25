# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from elasticsearch.exceptions import ConnectionError

from search import elastic


class Command(BaseCommand):
    def handle(self, *args, **options):
        index = settings.ELASTIC_INDEX
        self.stdout.write('Deleting index %s' % index)

        try:
            elastic.indices.delete(index=index, ignore=404)
        except ConnectionError:
            raise CommandError('Elasticsearch cannot be found')
