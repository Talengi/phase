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

        # Bucket docs by category
        search.aggs['per_month'].bucket(
            'per_category',
            'terms',
            field='doc_category.raw'
        )

        # Count docs with a return code of 0
        search.aggs['per_month'].aggs['per_category'].bucket(
            'per_return_code',
            'terms',
            field='return_code'
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
        buckets['% of docs distributed late by DC'] = map(self.get_pc_late_distributed_docs, raw_buckets)
        buckets['Nb of docs reviewed by leader'] = map(self.get_nb_leader_reviewed_docs, raw_buckets)
        buckets['Nb of docs reviewed late by leader'] = map(self.get_nb_late_leader_reviewed_docs, raw_buckets)
        buckets['% of docs reviewed late by Leader'] = map(self.get_pc_late_leader_reviewed_docs, raw_buckets)
        buckets['Nb of docs with return code 0'] = map(self.get_nb_return_code_zero, raw_buckets)
        buckets['Nb of TR docs in RC1'] = map(self.get_nb_tr_docs_in_rc(1), raw_buckets)
        buckets['Nb of TR docs in RC2'] = map(self.get_nb_tr_docs_in_rc(2), raw_buckets)
        buckets['Nb of TR docs in RC3'] = map(self.get_nb_tr_docs_in_rc(3), raw_buckets)
        buckets['Nb of vendor docs in RC1'] = map(self.get_nb_vendor_docs_in_rc(1), raw_buckets)
        buckets['Nb of vendor docs in RC2'] = map(self.get_nb_vendor_docs_in_rc(2), raw_buckets)
        buckets['Nb of vendor docs in RC3'] = map(self.get_nb_vendor_docs_in_rc(3), raw_buckets)

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

    def get_nb_return_code_zero(self, bucket):
        nb = 0
        cat_buckets = bucket['per_category']['buckets']
        for cat_bucket in cat_buckets:
            code_buckets = cat_bucket['per_return_code']['buckets']
            zero_bucket = next((b for b in code_buckets if b['key'] == 0), None)
            nb += zero_bucket['doc_count'] if zero_bucket else 0

        return nb

    def get_tr_bucket(self, bucket):
        buckets = bucket['per_category']['buckets']
        bucket = next((b for b in buckets if b['key'] == 'Contractor Deliverable'), None)
        return bucket

    def get_vendor_bucket(self, bucket):
        buckets = bucket['per_category']['buckets']
        bucket = next((b for b in buckets if b['key'] == 'Supplier Deliverable'), None)
        return bucket

    def get_nb_tr_docs_in_rc(self, code):
        def do_get_nb_tr_docs_in_rc(bucket):
            bucket = self.get_tr_bucket(bucket)
            bucket = bucket['per_return_code']['buckets'] if bucket else []
            bucket = next((b for b in bucket if b['key'] == code), None)
            return bucket['doc_count'] if bucket else 0
        return do_get_nb_tr_docs_in_rc

    def get_nb_vendor_docs_in_rc(self, code):
        def do_get_nb_vendor_docs_in_rc(bucket):
            bucket = self.get_vendor_bucket(bucket)
            bucket = bucket['per_return_code']['buckets'] if bucket else []
            bucket = next((b for b in bucket if b['key'] == code), None)
            return bucket['doc_count'] if bucket else 0
        return do_get_nb_vendor_docs_in_rc


class ReturnedDocsDashboardView(BaseDashboardView):
    es_document_type = 'epc2_documents.epc2deliverable'

    def _fetch_raw_data(self):
        search = Search(using=elastic, doc_type=self.es_document_type) \
            .index(settings.ELASTIC_INDEX) \
            .params(search_type='count')

        # Return only those stored fields
        search = search.fields(['document_key', 'received_date', 'review_sent_date'])

        # Group documents by month
        search.aggs.bucket(
            'per_month',
            'date_histogram',
            field='outgoing_trs_sent_date',
            interval='month',
            min_doc_count=0)

        # Bucket those docs by category
        search.aggs['per_month'].bucket(
            'per_category',
            'terms',
            field='doc_category.raw'
        )

        # For each month, select only docs with a the return information
        search.aggs['per_month'].aggs['per_category'].bucket(
            'with_return_info',
            'filter',
            filter={
                'and': {
                    'filters': [
                        {'exists': {'field': 'outgoing_trs_sent_date'}},
                        {'exists': {'field': 'review_due_date'}}
                    ]
                }
            })

        # For each month, compute the raw number of late documents
        search.aggs['per_month'] \
            .aggs['per_category'] \
            .aggs['with_return_info'].bucket(
                'late_docs',
                'filter',
                filter={
                    'script': {
                        'script': "doc['outgoing_trs_sent_date'].value > doc['review_due_date'].value"
                    }
                }
        )

        # For each bucket, comptue the average overdue
        search.aggs['per_month'] \
            .aggs['per_category'] \
            .aggs['with_return_info'] \
            .aggs['late_docs'].metric(
                'avg_overdue',
                'avg',
                script="doc['outgoing_trs_sent_date'].value - doc['review_due_date'].value"
        )

        # For each bucket, comptue the average overdue
        search.aggs['per_month'] \
            .aggs['per_category'] \
            .aggs['with_return_info'] \
            .aggs['late_docs'].metric(
                'avg_review_time',
                'avg',
                script="doc['outgoing_trs_sent_date'].value - doc['received_date'].value"
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
        buckets['TR Deliverables'] = map(self.get_nb_tr_docs, raw_buckets)
        buckets['Vendor Deliverables'] = map(self.get_nb_vendor_docs, raw_buckets)
        buckets['TOTAL'] = map(lambda x: x['doc_count'], raw_buckets)
        buckets['Avg nb of docs returned by day'] = map(lambda x: x['doc_count'] / 20.0, raw_buckets)
        buckets['% of docs returned late by GTG'] = map(self.get_pc_docs_returned_late_by_gtg, raw_buckets)
        buckets['% of TR docs returned late by GTG'] = map(self.get_pc_tr_docs_returned_late_by_gtg, raw_buckets)
        buckets['Average lead time for review for TR documents'] = map(self.get_avg_tr_review_time, raw_buckets)
        buckets['Average NB of days overdue for TR documents'] = map(self.get_avg_tr_overdue, raw_buckets)
        buckets['% of Vendor docs returned late by GTG'] = map(self.get_pc_vendor_docs_returned_late_by_gtg, raw_buckets)
        buckets['Average lead time for review for vendor documents'] = map(self.get_avg_vendor_review_time, raw_buckets)
        buckets['Average NB of days overdue for vendor documents'] = map(self.get_avg_vendor_overdue, raw_buckets)

        return buckets

    def format_pc(self, num, denum):
        try:
            res = 100.0 * float(num) / float(denum)
            res = '{:.2f}%'.format(res)
        except:
            res = 'ND'
        return res

    def get_tr_bucket(self, bucket):
        buckets = bucket['per_category']['buckets']
        bucket = next((b for b in buckets if b['key'] == 'Contractor Deliverable'), None)
        return bucket

    def get_vendor_bucket(self, bucket):
        buckets = bucket['per_category']['buckets']
        bucket = next((b for b in buckets if b['key'] == 'Supplier Deliverable'), None)
        return bucket

    def get_nb_tr_docs(self, bucket):
        bucket = self.get_tr_bucket(bucket)
        return bucket['doc_count'] if bucket else 0

    def get_nb_vendor_docs(self, bucket):
        bucket = self.get_vendor_bucket(bucket)
        return bucket['doc_count'] if bucket else 0

    def get_nb_late_tr_docs(self, bucket):
        bucket = self.get_tr_bucket(bucket)
        return bucket['with_return_info']['late_docs']['doc_count'] if bucket else 0

    def get_nb_late_vendor_docs(self, bucket):
        bucket = self.get_vendor_bucket(bucket)
        return bucket['with_return_info']['late_docs']['doc_count'] if bucket else 0

    def get_nb_late_docs(self, bucket):
        return self.get_nb_late_tr_docs(bucket) + self.get_nb_late_vendor_docs(bucket)

    def get_pc_docs_returned_late_by_gtg(self, bucket):
        nb_docs = bucket['doc_count']
        nb_late = self.get_nb_late_docs(bucket)
        return self.format_pc(nb_late, nb_docs)

    def get_pc_tr_docs_returned_late_by_gtg(self, bucket):
        nb_docs = self.get_nb_tr_docs(bucket)
        nb_late = self.get_nb_late_tr_docs(bucket)
        return self.format_pc(nb_late, nb_docs)

    def get_pc_vendor_docs_returned_late_by_gtg(self, bucket):
        nb_docs = self.get_nb_vendor_docs(bucket)
        nb_late = self.get_nb_late_vendor_docs(bucket)
        return self.format_pc(nb_late, nb_docs)

    def get_avg_tr_review_time(self, bucket):
        bucket = self.get_tr_bucket(bucket)
        avg = bucket['with_return_info']['late_docs']['avg_review_time']['value'] if bucket else 0
        return int(avg) / 86400000

    def get_avg_vendor_review_time(self, bucket):
        bucket = self.get_vendor_bucket(bucket)
        avg = bucket['with_return_info']['late_docs']['avg_review_time']['value'] if bucket else 0
        return int(avg) / 86400000

    def get_avg_tr_overdue(self, bucket):
        bucket = self.get_tr_bucket(bucket)
        avg = bucket['with_return_info']['late_docs']['avg_overdue']['value'] if bucket else 0
        return int(avg) / 86400000

    def get_avg_vendor_overdue(self, bucket):
        bucket = self.get_vendor_bucket(bucket)
        avg = bucket['with_return_info']['late_docs']['avg_overdue']['value'] if bucket else 0
        return int(avg) / 86400000
