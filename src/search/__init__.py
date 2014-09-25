# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.conf import settings

from elasticsearch import Elasticsearch


elastic = Elasticsearch(settings.ELASTIC_HOSTS)


# TODO On migration to Django 1.7, see
# http://stackoverflow.com/a/22924754/665797
import signals  # noqa
