# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class DashboardProvider(object):
    es_date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, **kwargs):
        self.category = kwargs.get('category', None)

    def query_elasticsearch(self):
        """Performs actual query to Elastic Search.

        The method must return a dict, as in the `to_dict` function of the
        python elastic search api.

        """
        raise NotImplemented()

    def fetch_data(self):
        """Sends a request to ES, and save the response in local variables."""
        data = self.query_elasticsearch()
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


class EmptyDashboard(DashboardProvider):
    pass
