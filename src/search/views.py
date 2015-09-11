# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import csv
from collections import OrderedDict

from django.db import models
from django.http import HttpResponse
from django.forms import ModelChoiceField
from django.utils.encoding import smart_bytes

from elasticsearch_dsl import Search
from braces.views import JSONResponseMixin

from search import elastic
from documents.views import BaseDocumentList
from documents.forms.filters import filterform_factory
from django.conf import settings


class BaseSearchView(BaseDocumentList):

    def get_queryset(self):
        """Given DataTables' GET parameters, filter the initial queryset."""
        queryset = super(BaseSearchView, self).get_queryset()
        FilterForm = filterform_factory(queryset.model)
        form = FilterForm(self.request.GET)
        if form.is_valid():
            s = self.build_search_query(
                queryset.model,
                self.category.document_type(),
                form)
            response = s.execute()

            return response

        return []

    def build_search_query(self, Model, document_type, form):
        """Builds an elasticsearch query."""

        s = Search(using=elastic, doc_type=document_type) \
            .index(settings.ELASTIC_INDEX) \
            .filter('term', is_latest_revision=True)

        data = form.cleaned_data

        # Filter fields
        filter_fields = Model.PhaseConfig.filter_fields
        for field in filter_fields:
            value = data.get(field, None)
            if value:
                if isinstance(value, models.Model):
                    value = value.pk
                    field = '%s_id' % field
                else:
                    field = '%s.raw' % field
                s = s.filter({'term': {field: value}})

        # Custom filters
        custom_filters = getattr(Model.PhaseConfig, 'custom_filters', {})
        for filter_key, filter_data in custom_filters.items():
            value = data.get(filter_key, None)
            f = filter_data['filters'].get(value, None)
            if f is not None:
                s = s.filter(f)

        # Aggregations (facets)
        # For foreign key fields, we need to organize buckets by primary keys
        # For every other field, the ".raw" field is what we want
        for field in filter_fields:
            if isinstance(form.fields[field], ModelChoiceField):
                s.aggs.bucket(field, 'terms', field='%s_id' % field, size=0)
            else:
                s.aggs.bucket(field, 'terms', field='%s.raw' % field, size=0)

        # Search query
        search_terms = data.get('search_terms', None)
        search_fields = Model.PhaseConfig.searchable_fields
        raw_search_fields = map(lambda x: '%s.raw' % x, search_fields)
        if search_terms:
            s = s.query({
                'multi_match': {
                    'query': search_terms,
                    'fields': ['_all'] + raw_search_fields,
                    'operator': 'and'
                }
            })

        # Sort query
        sort_field = data.get('sort_by', 'document_key') or 'document_key'
        sort_field = '%s.raw' % sort_field
        if sort_field.startswith('-'):
            sort_field = sort_field.lstrip('-')
            sort_direction = 'desc'
        else:
            sort_direction = 'asc'
        s = s.sort({sort_field: {'order': sort_direction}})

        # Pagination
        s = s.extra(
            from_=data.get('start', 0),
            size=data.get('size', settings.PAGINATE_BY)
        )

        return s


class SearchDocuments(JSONResponseMixin, BaseSearchView):
    http_method_names = ['get']

    def render_to_response(self, context, **response_kwargs):
        return self.render_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        response = self.get_queryset()
        start = int(self.request.GET.get('start', 0))
        end = start + int(self.request.GET.get('length', settings.PAGINATE_BY))
        total = response.hits.total
        display = min(end, total)
        search_data = [hit._d_ for hit in response.hits]
        aggregations = self.format_aggregations(response.aggregations)

        return {
            'total': total,
            'display': display,
            'data': search_data,
            'aggregations': aggregations,
        }

    def format_aggregations(self, aggregations):
        """Transfroms the ES "aggregations" response into something we can use.

        aggregations = {
            'filter_name': {
                'buckets': [
                    {'key': 'some_name', 'doc_count': 123},
                    …
                ]
            },
            …
        }

        We want :

        aggregations = {
            'filter_name': [{'some_name': 123}, …],
            …
        }

        """
        def flatten(bucket):
            key = bucket[0]
            buckets = bucket[1]['buckets']
            bucket_values = dict([(b['key'], b['doc_count']) for b in buckets])
            return (key, bucket_values)
        buckets = aggregations.to_dict().items()
        response = dict(map(flatten, buckets))
        return response


class ExportDocuments(BaseSearchView):
    """Query documents and export them to csv.

    There is a technical gotcha here. Since we use the document list filter
    syntax to retrieve document, the search has to be performed with
    elasticsearch.

    However, we want to export all the document's' fields, not only the one
    indexed. Thus, we have to get the data from the db, which necessitates
    a second query.

    This is not extremely elegant.

    An alternative solution would be to store whole documents in ES. I'm not
    sure which one is better.

    """
    def build_search_query(self, Model, document_type, form):
        """Build the ES query.

        Since actual data will be retrieved from db, we only need to
        get document ids to pass along.

        """
        query = super(ExportDocuments, self).build_search_query(
            Model, document_type, form)
        query = query.fields(['pk'])
        return query

    def get_documents(self):
        query = self.get_queryset()
        hits = query.hits
        pks = [hit['pk'][0] for hit in hits]

        Model = self.category.revision_class()
        qs = Model.objects \
            .filter(pk__in=pks) \
            .select_related()
        return qs

    def get_csv_header(self, form, revision_form):
        labels = [(key, '{}'.format(field.label)) for key, field in form.fields.items()]
        labels += [(key, '{}'.format(field.label)) for key, field in revision_form.fields.items()]
        return OrderedDict(labels)

    def get_csv_line(self, revision, form, revision_form):

        def val(obj, name):
            value = getattr(obj, name)
            return smart_bytes(value)

        metadata = revision.metadata
        values = [
            (field.name, val(metadata, field.name)) for field in form]

        values += [
            (field.name, val(revision, field.name)) for field in revision_form]

        return dict(values)

    def get_forms(self):
        Form = self.category.get_metadata_form_class()
        form = Form(category=self.category)

        RevisionForm = self.category.get_revision_form_class()
        revision_form = RevisionForm(category=self.category)

        return form, revision_form

    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(
            self.category.document_type())

        form, revision_form = self.get_forms()

        # Writer row header
        header = self.get_csv_header(form, revision_form)
        writer = csv.DictWriter(response, fieldnames=header.keys())
        writer.writerow(header)

        # Fetch documents from ES + DB
        revisions = self.get_documents()

        # Write csv data
        for revision in revisions:
            row = self.get_csv_line(revision, form, revision_form)
            writer.writerow(row)

        return response
