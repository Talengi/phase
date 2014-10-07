# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from elasticsearch.exceptions import ConnectionError

from search import elastic

INDEX_SETTINGS = {
    "settings": {
        "analysis": {
            "filter": {
                "nGram_filter": {
                    "type": "nGram",
                    "min_gram": 2,
                    "max_gram": 40,
                    "token_chars": [
                        "letter",
                        "digit",
                        "punctuation",
                        "symbol"
                    ]
                }
            },
            "analyzer": {
                "nGram_analyzer": {
                    "type": "custom",
                    "tokenizer": "whitespace",
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "nGram_filter"
                    ]
                },
                "whitespace_analyzer": {
                    "type": "custom",
                    "tokenizer": "whitespace",
                    "filter": [
                        "lowercase",
                        "asciifolding"
                    ]
                }
            }
        }
    }
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        index = settings.ELASTIC_INDEX
        self.stdout.write('Creating index %s' % index)

        try:
            elastic.indices.create(index=index, ignore=400, body=INDEX_SETTINGS)
        except ConnectionError:
            raise CommandError('Elasticsearch cannot be found')
