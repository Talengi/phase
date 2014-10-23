# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from elasticsearch.exceptions import ConnectionError

from search.utils import create_index


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Creating index %s' % settings.ELASTIC_INDEX)

        try:
            create_index()
        except ConnectionError:
            raise CommandError('Elasticsearch cannot be found')
