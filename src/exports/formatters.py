# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from documents.models import MetadataRevision
from transmittals.utils import FieldWrapper
from documents.utils import stringify_value as stringify
from exports.pdf import format_doc_as_pdf


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
        elif isinstance(doc, MetadataRevision):
            doc = FieldWrapper((
                doc,
                doc.document.metadata,
                doc.document))
            fields = self.fields.values()
            data = [self.get_field(doc, field) for field in fields]

        csv_data = '{}\n'.format(';'.join(data))
        return csv_data.encode('utf-8')

    def get_field(self, doc, field):
        data = getattr(doc, field, '')
        return stringify(data, none_val='')


class PDFFormatter(BaseFormatter):
    """Converts a queryset into pdf files."""

    def format_doc(self, doc):
        return format_doc_as_pdf(doc)
