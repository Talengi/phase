from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset

from documents.forms.models import BaseDocumentForm
from .models import ContractorDeliverable, ContractorDeliverableRevision
from .layout import (
    ScheduleLayout, ScheduleStatusLayout, FlatRelatedDocumentsLayout)


class ContractorDeliverableForm(BaseDocumentForm):
    def __init__(self, *args, **kwargs):
        super(ContractorDeliverableForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = self.build_layout()

    def build_layout(self):
        if self.read_only:
            related_documents = Fieldset(
                _('Related documents'),
                FlatRelatedDocumentsLayout('related_documents'),
            )
        else:
            related_documents = Fieldset(
                _('Related documents'),
                'related_documents',
            )

        return Layout(
            Fieldset(
                _('General information'),
                'document_key',
                'title',
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
            Fieldset(
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
        fields = ('document_key', 'title', 'contract_number', 'originator',
                  'unit', 'discipline', 'document_type', 'sequential_number',
                  'project_phase', 'klass', 'system', 'wbs', 'weight',
                  'related_documents', 'status_std_planned_date',
                  'status_idc_planned_date', 'status_ifr_planned_date',
                  'status_ifa_planned_date', 'status_ifd_planned_date',
                  'status_ifc_planned_date', 'status_ifi_planned_date',
                  'status_asb_planned_date', 'status_std_forecast_date',
                  'status_idc_forecast_date', 'status_ifr_forecast_date',
                  'status_ifa_forecast_date', 'status_ifd_forecast_date',
                  'status_ifc_forecast_date', 'status_ifi_forecast_date',
                  'status_asb_forecast_date', 'status_std_actual_date',
                  'status_idc_actual_date', 'status_ifr_actual_date',
                  'status_ifa_actual_date', 'status_ifd_actual_date',
                  'status_ifc_actual_date', 'status_ifi_actual_date',
                  'status_asb_actual_date')


class ContractorDeliverableRevisionForm(BaseDocumentForm):
    def __init__(self, *args, **kwargs):
        super(ContractorDeliverableRevisionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = self.build_layout()

    def build_layout(self):
        return Layout(
            Fieldset(
                _('Revision'),
                'status',
                #'revision_date',
                #'created_on',
                'final_revision',
                'native_file',
                'pdf_file',
            ),
            Fieldset(
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
        fields = ('status', 'final_revision', 'native_file', 'pdf_file',
                  'review_start_date', 'review_due_date', 'under_review',
                  'under_contractor_review', 'overdue', 'reviewers', 'leader',
                  'approver', 'under_gtg_review')
