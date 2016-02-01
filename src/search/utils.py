# -*- coding: utf8 -*-

from __future__ import unicode_literals

import logging

from django.db.models.fields import FieldDoesNotExist
from django.db import models

from elasticsearch.helpers import bulk
from elasticsearch.exceptions import ConnectionError

from core.celery import app
from categories.models import Category
from search import elastic, INDEX_SETTINGS
from documents.models import Document
from django.conf import settings


logger = logging.getLogger(__name__)


def refresh_index():
    """Make latest data available."""
    index = settings.ELASTIC_INDEX
    elastic.indices.refresh(index=index)


def create_index():
    """Create all needed indexes."""
    index = settings.ELASTIC_INDEX
    elastic.indices.create(index=index, ignore=400, body=INDEX_SETTINGS)


def delete_index():
    """Delete existing ES indexes."""
    index = settings.ELASTIC_INDEX
    elastic.indices.delete(index=index, ignore=404)


def index_revision(revision):
    """Saves a document's revision into ES's index."""
    document = revision.document
    es_key = '{}_{}'.format(document.document_key, revision.revision)
    try:
        elastic.index(
            index=settings.ELASTIC_INDEX,
            doc_type=document.document_type(),
            id=es_key,
            body=revision.to_json(),
        )
    except ConnectionError:
        logger.error('Error connecting to ES. The doc %d will no be indexed' %
                     es_key)


@app.task
def index_document(document_id):
    """Index all revisions for a document"""
    document = Document.objects \
        .select_related() \
        .get(pk=document_id)
    revisions = document.get_all_revisions()
    actions = map(build_index_data, revisions)

    bulk(
        elastic,
        actions,
        chunk_size=settings.ELASTIC_BULK_SIZE,
        request_timeout=60)


def index_revisions(revisions):
    """Index a bunch of revisions."""
    actions = map(build_index_data, revisions)
    bulk(
        elastic,
        actions,
        chunk_size=settings.ELASTIC_BULK_SIZE,
        request_timeout=60)


def bulk_actions(actions):
    bulk(
        elastic,
        actions,
        chunk_size=settings.ELASTIC_BULK_SIZE,
        request_timeout=60)


def build_index_data(revision):
    return {
        '_index': settings.ELASTIC_INDEX,
        '_type': revision.document.document_type(),
        '_id': revision.unique_id,
        '_source': revision.to_json(),
    }


@app.task
def unindex_document(document_id):
    """Removes all revisions of a document from the index."""
    document = Document.objects \
        .select_related() \
        .get(pk=document_id)
    revisions = document.get_all_revisions()
    actions = map(lambda revision: {
        '_op_type': 'delete',
        '_index': settings.ELASTIC_INDEX,
        '_type': document.document_type(),
        '_id': revision.unique_id,
    }, revisions)

    bulk(
        elastic,
        actions,
        raise_on_error=False,
        chunk_size=settings.ELASTIC_BULK_SIZE,
        request_timeout=60)


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
    column_fields = dict(config.column_fields).values()
    additional_fields = getattr(config, 'indexable_fields', [])
    fields = set(filter_fields + column_fields + additional_fields)

    for field_name in fields:
        try:
            field = doc_class._meta.get_field_by_name(field_name)[0]
        except FieldDoesNotExist:
            try:
                field = revision_class._meta.get_field_by_name(field_name)[0]
            except FieldDoesNotExist:
                field = getattr(doc_class, field_name, None)
                if field is None:
                    field = getattr(revision_class, field_name, None)
                    if field is None:
                        warning = 'Field {} cannot be found and will not be indexed'.format(field_name)
                        logger.warning(warning)

        es_type = get_mapping_type(field) if field else 'string'

        mapping['properties'].update({
            field_name: {
                'type': es_type,
                'include_in_all': field_name in column_fields,
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
