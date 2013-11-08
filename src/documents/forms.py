from django import forms
from django.conf import settings
from django.db.models.fields import BLANK_CHOICE_DASH

from documents.models import Document, DocumentRevision
from documents.constants import (
    DISCIPLINES, UNITS, DOCUMENT_TYPES, WBS, STATUSES, SYSTEMS,
)

date_attrs = {'class': "datepicker span2", 'data-date-format': "yyyy-mm-dd"}


class DocumentForm(forms.ModelForm):
    native_file = forms.FileField(
        label=u'Native file',
        required=False)
    pdf_file = forms.FileField(
        label=u'PDF file',
        required=False)

    class Meta:
        model = Document
        exclude = ('favorited_by',)
        widgets = {
            'document_number': forms.TextInput(attrs={
                'placeholder': 'Automatically generated if not specified.',
            }),
            'title': forms.Textarea(attrs={'rows': '2'}),
            'current_revision_date': forms.DateInput(attrs=date_attrs),
            'sequencial_number': forms.TextInput,
            'status_std_planned_date': forms.DateInput(attrs=date_attrs),
            'status_std_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_std_actual_date': forms.DateInput(attrs=date_attrs),
            'status_idc_planned_date': forms.DateInput(attrs=date_attrs),
            'status_idc_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_idc_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifr_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifr_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifr_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifa_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifa_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifa_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifd_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifd_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifd_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifc_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifc_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifc_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifi_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifi_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifi_actual_date': forms.DateInput(attrs=date_attrs),
            'status_asb_planned_date': forms.DateInput(attrs=date_attrs),
            'status_asb_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_asb_actual_date': forms.DateInput(attrs=date_attrs),
        }

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        # Automatically generated if empty
        self.fields['document_number'].required = False
        status_choices = [
            (status[0], u"{0} - {1}".format(status[0], status[1]))
            for status in STATUSES
        ]
        self.fields['status'].choices = status_choices
        discipline_choices = [
            (discipline[0], u"{0} - {1}".format(discipline[0], discipline[1]))
            for discipline in DISCIPLINES
        ]
        self.fields['discipline'].choices = discipline_choices
        unit_choices = [
            (unit[0], u"{0} - {1}".format(unit[0], unit[1]))
            for unit in UNITS
        ]
        self.fields['unit'].choices = unit_choices
        document_type_choices = [
            (doc_type[0], u"{0} - {1}".format(doc_type[0], doc_type[1]))
            for doc_type in DOCUMENT_TYPES
        ]
        self.fields['document_type'].choices = document_type_choices
        system_choices = [
            (system[0], u"{0} - {1}".format(system[0], system[1][:100]))
            for system in SYSTEMS
        ]
        self.fields['system'].choices = system_choices
        wbs_choices = [
            (wbs[0], u"{0} - {1}".format(wbs[0], wbs[1]))
            for wbs in WBS
        ]
        self.fields['wbs'].choices = wbs_choices

        documents = Document.objects.all()
        self.fields['related_documents'].choices = [
            (doc.pk, u"{0} - {1}".format(doc.document_number, doc.title))
            for doc in documents
        ]

    def clean_native_file(self):
        """Do not allow a PDF file to be uploaded as a native file.

        Checks both the content type and the filename.
        """
        native_file = self.cleaned_data['native_file']
        if native_file is not None and hasattr(native_file, 'content_type'):
            content_type = native_file.content_type
            if content_type == 'application/pdf'\
                    or native_file.name.endswith('.pdf'):
                raise forms.ValidationError(
                    'A PDF file is not allowed in this field.'
                )
        return native_file


class DocumentRevisionForm(forms.ModelForm):
    native_file = forms.FileField(
        label=u'Native file',
        required=False)
    pdf_file = forms.FileField(
        label=u'PDF file',
        required=False)

    class Meta:
        model = DocumentRevision
        date_attrs = {'class': "datepicker span2", 'data-date-format': "yyyy-mm-dd"}
        widgets = {
            'revision_date': forms.DateInput(attrs=date_attrs),
        }


class DocumentFilterForm(forms.ModelForm):
    """A form to check the validity of GET parameters from datatable."""
    length = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
        initial=settings.PAGINATE_BY)
    start = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
        initial=0)
    search_terms = forms.CharField(
        label=u'Search all columns',
        required=False)
    sort_by = forms.ChoiceField(
        choices=(
            ('document_number', 'document_number'),
            ('-document_number', '-document_number'),
            ('title', 'title'),
            ('-title', '-title'),
            ('current_revision', 'current_revision'),
            ('-current_revision', '-current_revision'),
            ('current_revision_date', 'current_revision_date'),
            ('-current_revision_date', '-current_revision_date'),
            ('status', 'status'),
            ('-status', '-status'),
        ),
        widget=forms.HiddenInput(),
        required=False,
        initial='document_number')

    class Meta:
        model = Document
        fields = (
            'search_terms', 'status', 'discipline', 'document_type',
            'unit', 'klass', 'contract_number', 'originator',
            'contractor_document_number', 'engineering_phase', 'feed_update',
            'system', 'wbs', 'under_ca_review', 'under_contractor_review',
            'leader', 'approver',
        )
        widgets = {
            'status_std_planned_date': forms.DateInput(attrs=date_attrs),
            'status_std_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_std_actual_date': forms.DateInput(attrs=date_attrs),
            'status_idc_planned_date': forms.DateInput(attrs=date_attrs),
            'status_idc_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_idc_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifr_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifr_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifr_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifa_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifa_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifa_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifd_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifd_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifd_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifc_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifc_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifc_actual_date': forms.DateInput(attrs=date_attrs),
            'status_ifi_planned_date': forms.DateInput(attrs=date_attrs),
            'status_ifi_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_ifi_actual_date': forms.DateInput(attrs=date_attrs),
            'status_asb_planned_date': forms.DateInput(attrs=date_attrs),
            'status_asb_forecast_date': forms.DateInput(attrs=date_attrs),
            'status_asb_actual_date': forms.DateInput(attrs=date_attrs),
        }

    def __init__(self, *args, **kwargs):
        super(DocumentFilterForm, self).__init__(*args, **kwargs)
        self.fields['discipline'].required = False
        self.fields['document_type'].required = False
        self.fields['klass'].required = False
        self.fields['unit'].required = False
        self.fields['contract_number'].required = False
        self.fields['originator'].required = False
        self.fields['engineering_phase'].required = False
        status_choices = [
            (status[0], u"{0} - {1}".format(status[0], status[1]))
            for status in STATUSES
        ]
        self.fields['status'].choices = status_choices
        discipline_choices = [
            (discipline[0], u"{0} - {1}".format(discipline[0], discipline[1]))
            for discipline in DISCIPLINES
        ]
        self.fields['discipline'].choices = discipline_choices
        unit_choices = [
            (unit[0], u"{0} - {1}".format(unit[0], unit[1]))
            for unit in UNITS
        ]
        self.fields['unit'].choices = unit_choices
        document_type_choices = [
            (doc_type[0], u"{0} - {1}".format(doc_type[0], doc_type[1]))
            for doc_type in DOCUMENT_TYPES
        ]
        self.fields['document_type'].choices = document_type_choices
        system_choices = [
            (system[0], u"{0} - {1}".format(system[0], system[1][:100]))
            for system in SYSTEMS
        ]
        self.fields['system'].choices = system_choices
        wbs_choices = [
            (wbs[0], u"{0} - {1}".format(wbs[0], wbs[1]))
            for wbs in WBS
        ]
        self.fields['wbs'].choices = wbs_choices
        for field_name in ('contract_number', 'originator', 'system',
                           'document_type', 'discipline', 'status',
                           'engineering_phase', 'klass', 'unit', 'wbs'):
            self.fields[field_name].choices = (
                BLANK_CHOICE_DASH +
                self.fields[field_name].choices
            )
            self.fields[field_name].initial = u''
        self.fields['status'].initial = u''
        self.fields['under_ca_review'].initial = u''


class DocumentDownloadForm(forms.Form):
    """A dummy form to check the validity of GET parameters for downloads."""
    document_ids = forms.ModelMultipleChoiceField(
        queryset=Document.objects.all(),
        to_field_name='id')
    format = forms.ChoiceField(
        choices=(
            ('pdf', "PDF format"),
            ('native', "Native format"),
            ('both', "Native + PDF formats"),
        ),
        required=False)
    revisions = forms.ChoiceField(
        choices=(
            ('latest', "Latest revision"),
            ('all', "All revisions"),
        ),
        required=False)
