from django.utils.translation import ugettext_lazy as _

from crispy_forms.layout import Layout, Field

from documents.forms.models import BaseDocumentForm
from .models import (
    ContractorDeliverable, ContractorDeliverableRevision,
    Correspondence, CorrespondenceRevision,
    MinutesOfMeeting, MinutesOfMeetingRevision,
    DemoMetadata, DemoMetadataRevision
)
from .layout import (
    DocumentFieldset, ScheduleLayout, ScheduleStatusLayout,
    FlatRelatedDocumentsLayout)


class ContractorDeliverableForm(BaseDocumentForm):
    def build_layout(self):
        if self.read_only:
            related_documents = DocumentFieldset(
                _('Related documents'),
                FlatRelatedDocumentsLayout('related_documents'),
            )
        else:
            related_documents = DocumentFieldset(
                _('Related documents'),
                'related_documents',
            )

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
                'project_phase',
                'klass',
                'system',
                'wbs',
                'weight',
            ),
            related_documents,
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
                #'revision_date',
                #'created_on',
                'final_revision',
                'native_file',
                'pdf_file',
            ),
            DocumentFieldset(
                _('Review'),
                'review_start_date',
                'review_due_date',
                'under_review',
                'under_contractor_review',
                'overdue',
                'reviewers',
                'leader',
                'leader_comments',
                'approver',
                'approver_comments',
                'under_gtg_review',
            )
        )

    class Meta:
        model = ContractorDeliverableRevision
        exclude = ('document', 'revision', 'revision_date', 'created_on',
                   'updated_on')


class CorrespondenceForm(BaseDocumentForm):
    def build_layout(self):
        if self.read_only:
            related_documents = DocumentFieldset(
                _('Related documents'),
                FlatRelatedDocumentsLayout('related_documents'),
            )
        else:
            related_documents = DocumentFieldset(
                _('Related documents'),
                'related_documents',
            )

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
                related_documents,
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
        exclude = ('document', 'revision', 'revision_date', 'created_on',
                   'updated_on')


class MinutesOfMeetingForm(BaseDocumentForm):
    def build_layout(self):
        if self.read_only:
            related_documents = DocumentFieldset(
                _('Response reference'),
                FlatRelatedDocumentsLayout('response_reference'),
            )
        else:
            related_documents = DocumentFieldset(
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
                related_documents,
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
                'native_file',
                'pdf_file',
            ),
        )

    class Meta:
        model = MinutesOfMeetingRevision
        exclude = ('document', 'revision', 'revision_date', 'created_on',
                   'updated_on')


class DemoMetadataForm(BaseDocumentForm):
    class Meta:
        model = DemoMetadata


class DemoMetadataRevisionForm(BaseDocumentForm):
    class Meta:
        model = DemoMetadataRevision
