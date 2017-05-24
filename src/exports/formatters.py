# -*- coding: utf-8 -*-

import datetime as dt

from documents.models import MetadataRevisionBase
from transmittals.utils import FieldWrapper
from documents.utils import stringify_value as stringify
import collections

# Only used in this module, it makes no sense to put it elsewhere for now
FR_DATE_FORMAT = '%d-%m-%Y'
FR_DATETIME_FORMAT = '%d-%m-%Y %H:%M'


class BaseFormatter(object):
    """Base class for all formatters.

    A formatter is a class responsible for converting raw data
    (i.e a queryset) into a format suitable for writing as is in
    a file.

    """
    def __init__(self, fields):
        self.fields = fields

    def _format(self, docs):
        """Converts the queryset data into the destination format.

        Must return binary data.

        """
        if docs is None:
            return b''
        formatted = []
        for doc in docs:
            formatted.append(self.format_doc(doc))
        return formatted

    def format(self, docs):
        return b''.join(self._format(docs))

    def format_doc(self, doc):
        raise NotImplementedError()


class CSVFormatter(BaseFormatter):
    """Converts a queryset into csv data."""

    def prepare_data(self, doc):
        if isinstance(doc, list):
            data = doc
        elif isinstance(doc, MetadataRevisionBase):
            doc = FieldWrapper((
                doc,
                doc.metadata,
                doc.metadata.document))
            fields = list(self.fields.values())
            data = [self.get_field(doc, field) for field in fields]
        return data

    def format_doc(self, doc):
        data = self.prepare_data(doc)

        # Some fields can contain new lines and break csv formatting so we
        # need to remove them (eg: document title TextField)
        csv_data = ';'.join(data).replace('\r\n', '').replace('\n', '')
        csv_data = '{}\n'.format(csv_data)
        return csv_data.encode('utf-8')

    def get_field(self, doc, field):
        data = getattr(doc, field, '')
        # Attributes and method can be passed
        if isinstance(data, collections.Callable):
            data = data()

        # We want dd-mm-yyy format for exports whereas
        if type(data) == dt.date:
            data = data.strftime(FR_DATE_FORMAT)

        if type(data) == dt.datetime:
            data = data.strftime(FR_DATETIME_FORMAT)

        return stringify(data, none_val='')


class XLSXFormatter(CSVFormatter):
    def format_doc(self, doc):
        return self.prepare_data(doc)

    def format(self, docs):
        return self._format(docs)
