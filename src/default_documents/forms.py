from django.utils.translation import ugettext_lazy as _
from django import forms

from crispy_forms.layout import Layout, Field
from crispy_forms.bootstrap import UneditableField

from documents.forms.models import BaseDocumentForm
from api.widgets import UserAutocomplete
from .models import (
    ContractorDeliverable, ContractorDeliverableRevision,
    Correspondence, CorrespondenceRevision,
    MinutesOfMeeting, MinutesOfMeetingRevision,
    Transmittals, TransmittalsRevision,
    DemoMetadata, DemoMetadataRevision
)
from .layout import (
    DocumentFieldset, ScheduleLayout, ScheduleStatusLayout,
    PropertyLayout, UneditableFile
)


class ContractorDeliverableForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('General information'),
                'document_key',
                Field('title', rows=2),
                'contract_number',
                'originator',
                'unit',
                'discipline',
                'document_type',
                'sequential_number',
                'klass',
                'system',
                'wbs',
                'weight',
            ),
            self.related_documents,
            DocumentFieldset(
                _('Schedule'),
                ScheduleLayout(
                    ScheduleStatusLayout('std'),
                    ScheduleStatusLayout('idc'),
                    ScheduleStatusLayout('ifr'),
                    ScheduleStatusLayout('ifa'),
                    ScheduleStatusLayout('ifd'),
                    ScheduleStatusLayout('ifc'),
                    ScheduleStatusLayout('ifi'),
                    ScheduleStatusLayout('asb'),
                )
            )
        )

    class Meta:
        model = ContractorDeliverable
        exclude = ('document', 'latest_revision')


class ContractorDeliverableRevisionForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('Revision'),
                'status',
                'final_revision',
                'native_file',
                'pdf_file',
            ),
            DocumentFieldset(
                _('Review'),
                UneditableField('review_start_date'),
                UneditableField('review_due_date'),
                PropertyLayout('current_review_step'),
                PropertyLayout('is_under_review'),
                PropertyLayout('is_overdue'),
                'reviewers',
                'leader',
                UneditableFile('leader_comments'),
                'approver',
                UneditableFile('approver_comments'),
            )
        )

    class Meta:
        model = ContractorDeliverableRevision
        exclude = ('document', 'revision', 'revision_date', 'created_on',
                   'updated_on')
        widgets = {
            'approver': UserAutocomplete,
            'leader': UserAutocomplete,
            'reviewers': forms.Select(),
        }


class CorrespondenceForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('General information'),
                'document_key',
                Field('subject', rows=2),
                'correspondence_date',
                'received_sent_date',
                'contract_number',
                'originator',
                'recipient',
                'document_type',
                'sequential_number',
                'author',
                'addresses',
                'response_required',
                'due_date',
                'external_reference',
                self.related_documents,
            )
        )

    class Meta:
        model = Correspondence
        exclude = ('document', 'latest_revision')


class CorrespondenceRevisionForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('Revision'),
                'status',
                'revision_date',
                'created_on',
                'native_file',
                'pdf_file',
            ),
            DocumentFieldset(
                _('Review'),
                'under_review',
                'overdue',
                'leader',
            )
        )

    class Meta:
        model = CorrespondenceRevision
        exclude = ('document', 'revision', 'updated_on')


class MinutesOfMeetingForm(BaseDocumentForm):
    def build_layout(self):
        if self.read_only:
            response_reference = DocumentFieldset(
                _('Response reference'),
                'response_reference',
            )
        else:
            response_reference = DocumentFieldset(
                _('Response reference'),
                'response_reference',
            )

        return Layout(
            DocumentFieldset(
                _('General information'),
                'document_key',
                Field('subject', rows=2),
                'meeting_date',
                'received_sent_date',
                'contract_number',
                'originator',
                'recipient',
                'document_type',
                'sequential_number',
                'prepared_by',
                'signed',
                response_reference,
            )
        )

    class Meta:
        model = MinutesOfMeeting
        exclude = ('document', 'latest_revision')


class MinutesOfMeetingRevisionForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('Revision'),
                'status',
                'revision_date',
                'created_on',
                'native_file',
                'pdf_file',
            ),
        )

    class Meta:
        model = MinutesOfMeetingRevision
        exclude = ('document', 'revision', 'updated_on')


class TransmittalsForm(BaseDocumentForm):
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
                'document_type',
                'sequential_number',
                'frm',
                'to',
                self.related_documents,
            )
        )

    class Meta:
        model = Transmittals
        exclude = ('document', 'latest_revision')


class TransmittalsRevisionForm(BaseDocumentForm):
    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('Revision'),
                'status',
                'revision_date',
                'created_on',
                'native_file',
                'pdf_file',
            ),
        )

    class Meta:
        model = TransmittalsRevision
        exclude = ('document', 'revision', 'updated_on')


class DemoMetadataForm(BaseDocumentForm):
    class Meta:
        model = DemoMetadata
        exclude = ('document', 'latest_revision')

    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('General information'),
                'document_key',
                Field('title', rows=2),
                self.related_documents,
            )
        )


class DemoMetadataRevisionForm(BaseDocumentForm):
    class Meta:
        model = DemoMetadataRevision
        exclude = ('document', 'revision', 'revision_date', 'created_on',
                   'updated_on')

    def build_layout(self):
        return Layout(
            DocumentFieldset(
                _('Revision'),
                'status',
                'native_file',
                'pdf_file',
            ),
            DocumentFieldset(
                _('Review'),
                UneditableField('review_start_date'),
                UneditableField('review_due_date'),
                PropertyLayout('is_under_review'),
                PropertyLayout('is_overdue'),
                'reviewers',
                'leader',
                'leader_comments',
                'approver',
                'approver_comments',
            )
        )
