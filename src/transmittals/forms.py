# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from crispy_forms.layout import Layout

from default_documents.layout import DocumentFieldset

from documents.forms.models import BaseDocumentForm
from transmittals.models import Transmittal, TransmittalRevision


class TransmittalForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('General information'),
                'document_key',
                'transmittal_date',
                'ack_of_receipt_date',
                'contract_number',
                'originator',
                'recipient',
                'sequential_number',
                self.related_documents,
            )
        )

    class Meta:
        model = Transmittal
        exclude = ('document', 'latest_revision', 'created_on', 'document_type')


class TransmittalRevisionForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('Revision'),
                'trs_status',
                'revision_date',
                'native_file',
                'pdf_file',
            ),
        )

    class Meta:
        model = TransmittalRevision
        exclude = ('document', 'revision', 'trs_status', 'created_on', 'updated_on')
