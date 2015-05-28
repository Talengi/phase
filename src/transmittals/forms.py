# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from crispy_forms.layout import Layout, Field

from default_documents.layout import DocumentFieldset

from documents.forms.models import BaseDocumentForm
from transmittals.models import Transmittal, TransmittalRevision


class TransmittalForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            Field('tobechecked_dir', type='hidden'),
            Field('accepted_dir', type='hidden'),
            Field('rejected_dir', type='hidden'),
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
        exclude = ('document', 'latest_revision', 'status', 'transmittal_key',
                   'document_type', 'contractor',)


class TransmittalRevisionForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('Revision'),
                'revision_date',
                Field('created_on', readonly='readonly'),
                'native_file',
                'pdf_file',
            ),
            DocumentFieldset(
                _('Review'),
                'received_date',
            ),
        )

    class Meta:
        model = TransmittalRevision
        exclude = ('document', 'revision', 'trs_status', 'updated_on')
