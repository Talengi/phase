# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import datetime
from collections import OrderedDict

from django.views.generic import TemplateView

from elasticsearch_dsl import Search

from search import elastic
from django.conf import settings


class BaseDashboardView(TemplateView):
    template_name = 'dashboards/dashboard.html'
    es_date_format = '%Y-%m-%dT%H:%M:%S.%fZ'


class DashboardView(BaseDashboardView):

    def get_search_data(self):
        document_type = 'epc2_documents.epc2supplierdeliverable'
        search = Search(using=elastic, doc_type=document_type) \
            .index(settings.ELASTIC_INDEX) \
            .params(search_type='count')

        search = search.fields(['document_key', 'received_date', 'review_sent_date'])

        search.update_from_dict({
            'script_fields': {
                'distribution_delay': {
                    'script': "doc['review_sent_date'].value - doc['received_date'].value"
                }
            }
        })

        search.aggs.bucket(
            'per_month',
            'date_histogram',
            field='received_date',
            interval='month',
            min_doc_count=0
        ).bucket(
            'with_a_sent_date',
            'filter',
            filter={
                'exists': {
                    'field': 'review_sent_date',
                }
            }
        ).metric(
            'nb_docs_with_late_distribution',
            'filter',
            filter={
                'script': {
                    'script': "doc['review_sent_date'].value != doc['received_date'].value"
                }
            }
        )

        return search.execute().to_dict()

    def get_dashboard_header(self, search_data):
        buckets = search_data['aggregations']['per_month']['buckets']
        headers = [datetime.datetime.strptime(bucket['key_as_string'], self.es_date_format) for bucket in buckets]
        return headers

    def generate_buckets(self, search_data):
        raw_buckets = search_data['aggregations']['per_month']['buckets']

        buckets = OrderedDict()
        buckets['TR Deliverables'] = map(lambda x: x['doc_count'], raw_buckets)
        buckets['Nb of distributed docs'] = map(self.get_distributed_docs, raw_buckets)
        buckets['Nb of docs distributed late'] = map(self.get_nb_late_docs, raw_buckets)
        buckets['% of docs reviewed late'] = map(self.get_pc_late_docs, raw_buckets)

        return buckets

    def get_distributed_docs(self, bucket):
        return bucket['with_a_sent_date']['doc_count']

    def get_nb_late_docs(self, bucket):
        return bucket['with_a_sent_date']['nb_docs_with_late_distribution']['doc_count']

    def get_pc_late_docs(self, bucket):
        nb_with_sent_date = bucket['with_a_sent_date']['doc_count']
        nb_late_docs = bucket['with_a_sent_date']['nb_docs_with_late_distribution']['doc_count']

        try:
            res = 100.0 * float(nb_late_docs) / float(nb_with_sent_date)
            res = '{:.2f}%'.format(res)
        except:
            res = 'ND'
        return res

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        data = self.get_search_data()
        dashboard_header = self.get_dashboard_header(data)
        buckets = self.generate_buckets(data)

        pretty_response = json.dumps(data, indent=4)
        context.update({
            'dashboard_header': dashboard_header,
            'pretty_response': pretty_response,
            'buckets': buckets,
        })

        return context
