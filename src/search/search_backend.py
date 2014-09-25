# -*- coding: utf8 -*-

from __future__ import unicode_literals

from search import elastic
from django.conf import settings


def index_document(document):
    metadata = document.metadata
    document_type = '%s.%s' % (metadata.__module__, metadata.__class__.__name__)
    elastic.index(
        index=settings.ELASTIC_INDEX,
        doc_type=document_type,
        id=document.pk,
        body=document.to_json()
    )
