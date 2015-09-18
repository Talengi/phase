# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from search.builder import SearchBuilder


class ExportGenerator(object):
    """Exports data based on query filters.

    Use Elasticsearch and the db to efficiently (as far as possible) fetch data
    from a certain category filtered by the given filters.

    Yields data in chunks.

    """
    def __init__(self, category, filters, fields):
        self.category = category
        self.fields = fields
        self.filters = filters
        self.filters.update({
            'start': 0,
            'size': 60000})

    def __iter__(self):
        self.pks, self.total = self.get_es_results()
        self.start = -1
        self.chunk_size = settings.EXPORTS_CHUNK_SIZE
        return self

    def get_es_results(self):
        """Perform initial doc search using elasticsearch.

        Only return document ids, since the actual data export will use db.

        """
        builder = SearchBuilder(self.category, self.filters)
        result = builder.get_results(['pk'])
        hits = result.hits
        pks = [hit['pk'][0] for hit in hits]
        total = hits.total
        return pks, total

    def __next__(self):
        return self.next()

    def next(self):
        return self.next_data_chunk()

    def next_data_chunk(self):
        """Actual next() implemenation.

        Must return the next formatted chunk of data to be
        dumped in the file.

        """
        if self.start == -1:
            self.start = 0
            return self.data_header()

        if self.start >= self.total:
            raise StopIteration()

        chunk = self.get_chunk()
        self.start += self.chunk_size
        return chunk

    def data_header(self):
        return

    def get_chunk(self):
        """Get a single piece of data."""
        Model = self.category.revision_class()
        pks = self.pks[self.start:self.start + self.chunk_size]
        qs = Model.objects \
            .filter(pk__in=pks) \
            .select_related()
        return qs


class CSVGenerator(ExportGenerator):
    def data_header(self):
        return [self.fields.keys()]
