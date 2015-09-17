# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class BaseFormatter(object):
    """Base class for all formatters.

    A formatter is a class responsible for converting raw data
    (i.e a queryset) into a format suitable for writing as is in
    a file.

    """
    def __init__(self, fields):
        self.fields = fields

    def format(self, qs):
        """Converts the queryset data into the destination format.

        Must return binary data.

        """
        formatted = []
        for doc in qs:
            formatted.append(self.format_doc(doc))

        return b''.join(formatted)

    def format_doc(self, doc):
        raise NotImplementedError()


class CSVFormatter(BaseFormatter):
    """Converts a queryset into csv data."""

    def format_doc(self, doc):
        fields = self.fields.values()
        data = [getattr(doc, field) for field in fields]
        csv_data = '{}\n'.format(';'.join(data))
        return csv_data.encode('utf-8')
