# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class BaseGenerator(object):
    """Exports data based on query filters.

    Use Elasticsearch and the db to efficiently (as far as possible) fetch data
    from a certain category filtered by the given filters.

    Yields data in chunks.

    """
    def __init__(self, category, filters={}):
        self.category = category
        self.filters = filters


class CSVGenerator(BaseGenerator):
    pass
