# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class BaseGenerator(object):
    """Exports data based on query filters.

    Use Elasticsearch and the db to efficiently (as far as possible) fetch data
    from a certain category filtered by the given querystring.

    Yields data in chunks.

    """
    def __init__(self, category, querystring=''):
        self.category = category
        self.querystring = querystring


class CSVGenerator(BaseGenerator):
    pass
