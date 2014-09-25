# -*- coding: utf8 -*-

from __future__ import unicode_literals

from search import elastic
from django.conf import settings


def index_document(document):
    elastic.index(
        index=settings.ELASTIC_INDEX,
        doc_type=document.document_type(),
        id=document.pk,
        body=document.to_json()
    )


def unindex_document(document):
    elastic.delete(
        index=settings.ELASTIC_INDEX,
        id=document.pk
    )
