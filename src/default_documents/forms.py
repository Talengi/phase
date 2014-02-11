from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from documents.forms.models import BaseDocumentForm
from .models import (
    ContractorDeliverable, ContractorDeliverableRevision, DemoMetadata,
    DemoMetadataRevision
)
from .layout import (
    DocumentFieldset, ScheduleLayout, ScheduleStatusLayout,
    FlatRelatedDocumentsLayout)


class ContractorDeliverableForm(BaseDocumentForm):
    def __init__(self, *args, **kwargs):
        super(ContractorDeliverableForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = self.build_layout()

        # Document key is automatically generated, this field should not be required
        self.fields['document_key'].required = False

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
    def __init__(self, *args, **kwargs):
        super(ContractorDeliverableRevisionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = self.build_layout()

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
                'approver',
                'under_gtg_review',
            )
        )

    class Meta:
        model = ContractorDeliverableRevision
        exclude = ('document', 'revision', 'revision_date', 'created_on',
                   'updated_on')


class DemoMetadataForm(BaseDocumentForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = DemoMetadata


class DemoMetadataRevisionForm(BaseDocumentForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = DemoMetadataRevision
