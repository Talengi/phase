# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from elasticsearch.exceptions import ConnectionError

from search.utils import delete_index


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Deleting index %s' % settings.ELASTIC_INDEX)

        try:
            delete_index()
        except ConnectionError:
            raise CommandError('Elasticsearch cannot be found')
