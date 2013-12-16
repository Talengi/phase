from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset

from .models import ContractorDeliverable
from .layout import ScheduleLayout, ScheduleStatusLayout


class ContractorDeliverableForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(
        Fieldset(
            _('General information'),
            'document_key',
            'title',
            'contract_number',
            'originator',
            'unit',
            'discipline',
            'document_type',
            #'sequential_number',  # TODO typo
            'project_phase',
            'klass',
            'system',
            'wbs',
            'weight',

        ),
        Fieldset(
            _('Related documents'),
            'related_documents',
        ),
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
