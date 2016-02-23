# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from documents.models import MetadataRevisionBase
from transmittals.utils import FieldWrapper
from documents.utils import stringify_value as stringify


class BaseFormatter(object):
    """Base class for all formatters.

    A formatter is a class responsible for converting raw data
    (i.e a queryset) into a format suitable for writing as is in
    a file.

    """
    def __init__(self, fields):
        self.fields = fields

    def format(self, docs):
        """Converts the queryset data into the destination format.

        Must return binary data.

        """
        if docs is None:
            return b''

        formatted = []
        for doc in docs:
            formatted.append(self.format_doc(doc))

        return b''.join(formatted)

    def format_doc(self, doc):
        raise NotImplementedError()


class CSVFormatter(BaseFormatter):
    """Converts a queryset into csv data."""

    def format_doc(self, doc):
        if isinstance(doc, list):
            data = doc
        elif isinstance(doc, MetadataRevisionBase):
            doc = FieldWrapper((
                doc,
                doc.document.metadata,
                doc.document))
            fields = self.fields.values()
            data = [self.get_field(doc, field) for field in fields]

        # Some fields can contain new lines and break csv formatting so we
        # need to remove them (eg: document title TextField)
        csv_data = ';'.join(data).replace('\r\n', '').replace('\n', '')
        csv_data = '{}\n'.format(csv_data)
        return csv_data.encode('utf-8')

    def get_field(self, doc, field):
        data = getattr(doc, field, '')
        # Attributes and method can be passed
        if callable(data):
            data = data()
        return stringify(data, none_val='')
