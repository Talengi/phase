# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.conf import settings

from elasticsearch import Elasticsearch


elastic = Elasticsearch(settings.ELASTIC_HOSTS)
