# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView

from elasticsearch_dsl import Search

from search import elastic
from django.conf import settings


class DashboardView(TemplateView):
    template_name = 'dashboards/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        document_type = 'epc2_documents.epc2supplierdeliverable'
        search = Search(using=elastic, doc_type=document_type) \
            .index(settings.ELASTIC_INDEX) \
            .params(search_type='count')

        s = Search()
        s.aggs.bucket('per_category', 'terms', field='category')\
            .metric('clicks_per_category', 'sum', field='clicks')\
            .bucket('tags_per_category', 'terms', field='tags')

        search.aggs.bucket(
            'per_month',
            'date_histogram',
            field='review_due_date',
            interval='month',
            min_doc_count=0
        ).metric(
            'avg_class',
            'avg',
            field='docclass')

        print search.to_dict()

        response = search.execute()
        context.update({
            'nb_documents': len(response.hits),
            'response': response,
            'aggregations': response.aggregations,

        })

        return context
