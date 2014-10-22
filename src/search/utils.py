# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging

from django.db.models.fields import FieldDoesNotExist
from django.db import models

from elasticsearch.exceptions import ConnectionError

from core.celery import app
from categories.models import Category
from search import elastic
from django.conf import settings


logger = logging.getLogger(__name__)


TYPE_MAPPING = [
    ((models.CharField, models.TextField), 'string'),
    ((models.IntegerField,), 'long'),
    ((models.DecimalField, models.FloatField,), 'double'),
    ((models.DateField, models.TimeField,), 'date'),
    ((models.BooleanField, models.NullBooleanField,), 'boolean'),
]


@app.task
def put_category_mapping(category_id):
    category = Category.objects \
        .select_related('organisation', 'category_template__metadata_model') \
        .get(pk=category_id)

    doc_class = category.document_class()
    doc_type = category.document_type()
    mapping = get_mapping(doc_class)
    elastic.indices.put_mapping(
        index=settings.ELASTIC_INDEX,
        doc_type=doc_type,
        body=mapping,
        ignore_conflicts=True
    )


def get_mapping(doc_class):
    """Creates an elasticsearch mapping for a given document class.

    See: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping.html

    Note: with elasticsearch, sorting cannot be done on "analyzed" values. We
    use multifields so fields can be indexed twice, one analyzed version, and
    one not_analyzed. Thus, we can search, filter, sort or query any field.

    See: http://www.elasticsearch.org/guide/en/elasticsearch/guide/current/multi-fields.html

    """
    revision_class = doc_class.get_revision_class()
    mapping = {
        '_all': {
            'index_analyzer': 'nGram_analyzer',
            'search_analyzer': 'whitespace_analyzer',
            'index': 'not_analyzed',
        },
        'properties': {}
    }

    config = doc_class.PhaseConfig
    filter_fields = list(config.filter_fields)
    searchable_fields = list(config.searchable_fields)
    column_fields = [field[1] for field in config.column_fields]
    fields = filter_fields + column_fields

    for field_name in fields:
        try:
            field = doc_class._meta.get_field_by_name(field_name)[0]
        except FieldDoesNotExist:
            try:
                field = revision_class._meta.get_field_by_name(field_name)[0]
            except FieldDoesNotExist:
                field = None

        es_type = get_mapping_type(field) if field else 'string'

        mapping['properties'].update({
            field_name: {
                'type': es_type,
                'include_in_all': field_name in searchable_fields,
                'fields': {
                    'raw': {
                        'type': es_type,
                        'index': 'not_analyzed',
                        'include_in_all': False
                    }
                }
            }
        })

    return mapping


def get_mapping_type(field):
    """Get the elasticsearch mapping type from a django field."""
    for typeinfo, typename in TYPE_MAPPING:
        if isinstance(field, typeinfo):
            return typename
    return 'string'


@app.task
def index_document(document_id, document_type, document_json):
    """Stores a document into the ES index."""
    try:
        elastic.index(
            index=settings.ELASTIC_INDEX,
            doc_type=document_type,
            id=document_id,
            body=document_json,
        )
    except ConnectionError:
        logger.error('Error connecting to ES. The doc %d will no be indexed' % document_id)


@app.task
def unindex_document(document_id, document_type):
    """Removes the document from the index."""
    try:
        elastic.delete(
            index=settings.ELASTIC_INDEX,
            doc_type=document_type,
            id=document_id
        )
    except ConnectionError:
        logger.error('Error connecting to ES. The doc %d will no be un-indexed' % document_id)
