# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from collections import OrderedDict

from django.views.generic import TemplateView

from elasticsearch_dsl import Search

from search import elastic
from django.conf import settings


class BaseDashboardView(TemplateView):
    template_name = 'dashboards/dashboard.html'
    es_date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    es_document_type = None

    def _fetch_raw_data(self):
        """Performs actual query to Elastic Search.

        The method must return a dict, as in the `to_dict` function of the
        python elastic search api.

        """
        raise NotImplemented()

    def fetch_data(self):
        """Sends a request to ES, and save the response in local variables."""
        data = self._fetch_raw_data()
        self.hits = data['hits']['hits']
        self.total_hits = data['hits']['total']
        self.took = data['took']
        self.aggregations = data['aggregations']

    def get_headers(self):
        """Must return a list of dates."""
        raise NotImplemented()

    def get_buckets(self):
        """Return an ordered dict of data.

        Each key is a string, and is the name of the row.
        Each value is a list that contains as many values as there are headers.

        """
        raise NotImplemented()

    def get_context_data(self, **kwargs):
        context = super(BaseDashboardView, self).get_context_data(**kwargs)
        self.fetch_data()
        headers = self.get_headers()
        buckets = self.get_buckets()

        context.update({
            'headers': headers,
            'buckets': buckets,
        })

        return context


class IssuedDocsDashboardView(BaseDashboardView):
    es_document_type = 'epc2_documents.epc2deliverable'

    def _fetch_raw_data(self):
        search = Search(using=elastic, doc_type=self.es_document_type) \
            .index(settings.ELASTIC_INDEX) \
            .params(search_type='count')

        # Return only those stored fields
        search = search.fields(['document_key', 'received_date', 'review_sent_date'])

        # Group documents by month on the `received_date` field
        search.aggs.bucket(
            'per_month',
            'date_histogram',
            field='received_date',
            interval='month',
            min_doc_count=0)

        # For each month, count docs for each category
        search.aggs['per_month'].bucket(
            'per_category',
            'terms',
            field='doc_category.raw')

        # For each month, select only docs with a `review_sent_date` field
        search.aggs['per_month'].bucket(
            'with_a_sent_date',
            'filter',
            filter={
                'exists': {
                    'field': 'review_sent_date',
                }
            })

        # Among those docs, compute the raw number of late documents
        search.aggs['per_month'].aggs['with_a_sent_date'].metric(
            'nb_docs_with_late_distribution',
            'filter',
            filter={
                'script': {
                    'script': "doc['review_sent_date'].value > doc['received_date'].value"
                }
            }
        )

        # For each month, select only docs with a `leader_comment_date` field
        search.aggs['per_month'].bucket(
            'with_a_leader_comment',
            'filter',
            filter={
                'exists': {
                    'field': 'leader_step_closed',
                }
            })

        # Among those docs, compute the raw number of late documents
        search.aggs['per_month'].aggs['with_a_leader_comment'].metric(
            'nb_docs_with_late_leader_review',
            'filter',
            filter={
                'script': {
                    'script': "doc['leader_step_closed'].value > doc['review_due_date'].value"
                }
            }
        )

        res = search.execute()
        res_dict = res.to_dict()
        return res_dict

    def get_headers(self):
        buckets = self.aggregations['per_month']['buckets']
        headers = [datetime.datetime.strptime(bucket['key_as_string'], self.es_date_format) for bucket in buckets]
        return headers

    def get_buckets(self):
        raw_buckets = self.aggregations['per_month']['buckets']

        buckets = OrderedDict()
        buckets['TR Deliverables'] = map(self.get_nb_tr_deliverables, raw_buckets)
        buckets['Vendor Deliverables'] = map(self.get_nb_vendor_deliverables, raw_buckets)
        buckets['TOTAL'] = map(lambda x: x['doc_count'], raw_buckets)
        buckets['Avg docs received by day'] = map(lambda x: x['doc_count'] / 20.0, raw_buckets)
        buckets['Nb of distributed docs'] = map(self.get_nb_distributed_docs, raw_buckets)
        buckets['Nb of docs distributed late'] = map(self.get_nb_late_distributed_docs, raw_buckets)
        buckets['% of docs distributed late'] = map(self.get_pc_late_distributed_docs, raw_buckets)
        buckets['Nb of docs reviewed by leader'] = map(self.get_nb_leader_reviewed_docs, raw_buckets)
        buckets['Nb of docs reviewed late by leader'] = map(self.get_nb_late_leader_reviewed_docs, raw_buckets)
        buckets['% of docs reviewed late by leader'] = map(self.get_pc_late_leader_reviewed_docs, raw_buckets)

        return buckets

    def get_nb_tr_deliverables(self, bucket):
        category_bucket = bucket['per_category']['buckets']
        data = next((x for x in category_bucket if x['key'] == 'Contractor Deliverable'), None)
        return data['doc_count'] if data else 0

    def get_nb_vendor_deliverables(self, bucket):
        category_bucket = bucket['per_category']['buckets']
        data = next((x for x in category_bucket if x['key'] == 'Supplier Deliverable'), None)
        return data['doc_count'] if data else 0

    def get_nb_distributed_docs(self, bucket):
        return bucket['with_a_sent_date']['doc_count']

    def get_nb_late_distributed_docs(self, bucket):
        return bucket['with_a_sent_date']['nb_docs_with_late_distribution']['doc_count']

    def get_pc_late_distributed_docs(self, bucket):
        nb_with_sent_date = bucket['with_a_sent_date']['doc_count']
        nb_late_docs = bucket['with_a_sent_date']['nb_docs_with_late_distribution']['doc_count']

        try:
            res = 100.0 * float(nb_late_docs) / float(nb_with_sent_date)
            res = '{:.2f}%'.format(res)
        except:
            res = 'ND'
        return res

    def get_nb_leader_reviewed_docs(self, bucket):
        return bucket['with_a_leader_comment']['doc_count']

    def get_nb_late_leader_reviewed_docs(self, bucket):
        return bucket['with_a_leader_comment']['nb_docs_with_late_leader_review']['doc_count']

    def get_pc_late_leader_reviewed_docs(self, bucket):
        nb_docs = bucket['with_a_sent_date']['doc_count']
        nb_late_docs = bucket['with_a_leader_comment']['nb_docs_with_late_leader_review']['doc_count']

        try:
            res = 100.0 * float(nb_late_docs) / float(nb_docs)
            res = '{:.2f}%'.format(res)
        except:
            res = 'ND'
        return res


class ReturnedDocsDashboardView(BaseDashboardView):
    es_document_type = 'epc2_documents.epc2deliverable'

    def _fetch_raw_data(self):
        search = Search(using=elastic, doc_type=self.es_document_type) \
            .index(settings.ELASTIC_INDEX) \
            .params(search_type='count')

        # Return only those stored fields
        search = search.fields(['document_key', 'received_date', 'review_sent_date'])

        # Add dynamic fields computed on the fly
        search.update_from_dict({
            'script_fields': {
                'return_delay': {
                    'script': "doc['review_sent_date'].value - doc['review_due_date'].value"
                }
            }
        })

        # Group documents by month on the `received_date` field
        search.aggs.bucket(
            'per_month',
            'date_histogram',
            field='review_sent_date',
            interval='month',
            min_doc_count=0)

        # For each month, select only docs with a `leader_comment_date` field
        search.aggs['per_month'].bucket(
            'docs_with_return_information',
            'filter',
            filter={
                'and': {
                    'filters': [
                        {'exists': {'field': 'review_sent_date'}},
                        {'exists': {'field': 'review_due_date'}}
                    ]
                }
            })

        # For each month, count docs for each category
        search.aggs['per_month'].bucket(
            'per_category',
            'terms',
            field='doc_category.raw')

        # For each month, compute the raw number of late documents
        search.aggs['per_month'].bucket(
            'nb_docs_returned_late',
            'filter',
            filter={
                'script': {
                    'script': "doc['review_sent_date'].value > doc['review_due_date'].value"
                }
            }
        )

        # Bucket those late docs by category
        search.aggs['per_month'].aggs['nb_docs_returned_late'].bucket(
            'per_category',
            'terms',
            field='doc_category.raw'
        )

        # Count docs with a return code of 0
        search.aggs['per_month'].metric(
            'nb_docs_with_return_code_zero',
            'filter',
            filter={
                'term': {'return_code': 0}
            })

        res = search.execute()
        res_dict = res.to_dict()
        return res_dict

    def get_headers(self):
        buckets = self.aggregations['per_month']['buckets']
        headers = [datetime.datetime.strptime(bucket['key_as_string'], self.es_date_format) for bucket in buckets]
        return headers

    def get_buckets(self):
        raw_buckets = self.aggregations['per_month']['buckets']

        buckets = OrderedDict()
        buckets['TR Deliverables'] = map(self.get_nb_tr_deliverables, raw_buckets)
        buckets['Vendor Deliverables'] = map(self.get_nb_vendor_deliverables, raw_buckets)
        buckets['TOTAL'] = map(lambda x: x['doc_count'], raw_buckets)
        buckets['Avg nb of docs returned by day'] = map(lambda x: x['doc_count'] / 20.0, raw_buckets)
        buckets['% of docs returned late by GTG'] = map(self.get_pc_docs_returned_late_by_gtg, raw_buckets)
        buckets['% of TR docs returned late by GTG'] = map(self.get_pc_tr_docs_returned_late_by_gtg, raw_buckets)
        buckets['% of Vendor docs returned late by GTG'] = map(self.get_pc_vendor_docs_returned_late_by_gtg, raw_buckets)

        buckets['Nb of docs with return code 0'] = map(self.get_nb_return_code_zero, raw_buckets)

        return buckets

    def get_nb_tr_deliverables(self, bucket):
        buckets = bucket['per_category']['buckets']
        data = next((b for b in buckets if b['key'] == 'Contractor Deliverable'), None)
        return data['doc_count'] if data else 0

    def get_nb_vendor_deliverables(self, bucket):
        buckets = bucket['per_category']['buckets']
        data = next((b for b in buckets if b['key'] == 'Supplier Deliverable'), None)
        return data['doc_count'] if data else 0

    def get_pc_docs_returned_late_by_gtg(self, bucket):
        nb_late = bucket['nb_docs_returned_late']['doc_count']
        nb_docs = bucket['docs_with_return_information']['doc_count']
        try:
            res = 100.0 * float(nb_late) / float(nb_docs)
            res = '{:.2f}%'.format(res)
        except:
            res = 'ND'
        return res

    def get_pc_tr_docs_returned_late_by_gtg(self, bucket):
        nb_docs = bucket['docs_with_return_information']['doc_count']

        buckets = bucket['nb_docs_returned_late']['per_category']['buckets']
        data = next((b for b in buckets if b['key'] == 'Contractor Deliverable'), None)
        nb_late = data['doc_count'] if data else 0

        try:
            res = 100.0 * float(nb_late) / float(nb_docs)
            res = '{:.2f}%'.format(res)
        except:
            res = 'ND'
        return res

    def get_pc_vendor_docs_returned_late_by_gtg(self, bucket):
        nb_docs = bucket['docs_with_return_information']['doc_count']

        buckets = bucket['nb_docs_returned_late']['per_category']['buckets']
        data = next((b for b in buckets if b['key'] == 'Supplier Deliverable'), None)
        nb_late = data['doc_count'] if data else 0

        try:
            res = 100.0 * float(nb_late) / float(nb_docs)
            res = '{:.2f}%'.format(res)
        except:
            res = 'ND'
        return res

    def get_nb_return_code_zero(self, bucket):
        return bucket['nb_docs_with_return_code_zero']['doc_count']
