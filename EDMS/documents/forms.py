
from django import forms

from documents.models import Document
from documents.constants import (
    DISCIPLINES, UNITS, DOCUMENT_TYPES, WBS, STATUSES
)


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        date_attrs = {'class': "datepicker span2", 'data-date-format': "yyyy-mm-dd"}
        widgets = {
            'document_number': forms.TextInput(attrs={
                'placeholder': 'Automatically generated if not specified.',
                'class': 'span4',
            }),
            'title': forms.Textarea(attrs={'rows': '2', 'class': 'span4'}),
            'revision_date': forms.DateInput(attrs=date_attrs),
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
        wbs_choices = [
            (wbs[0], u"{0} - {1}".format(wbs[0], wbs[1]))
            for wbs in WBS
        ]
        self.fields['wbs'].choices = wbs_choices

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


class DocumentFilterForm(forms.Form):
    """A dummy form to check the validity of GET parameters from DataTables."""
    bRegex = forms.BooleanField(required=False)
    bRegex_0 = forms.BooleanField(required=False)
    bRegex_1 = forms.BooleanField(required=False)
    bRegex_2 = forms.BooleanField(required=False)
    bRegex_3 = forms.BooleanField(required=False)
    bRegex_4 = forms.BooleanField(required=False)
    bRegex_5 = forms.BooleanField(required=False)
    bRegex_6 = forms.BooleanField(required=False)
    bRegex_7 = forms.BooleanField(required=False)
    bRegex_8 = forms.BooleanField(required=False)
    bSearchable_0 = forms.BooleanField()
    bSearchable_1 = forms.BooleanField()
    bSearchable_2 = forms.BooleanField()
    bSearchable_3 = forms.BooleanField()
    bSearchable_4 = forms.BooleanField()
    bSearchable_5 = forms.BooleanField()
    bSearchable_6 = forms.BooleanField()
    bSearchable_7 = forms.BooleanField()
    bSearchable_8 = forms.BooleanField()
    bSortable_0 = forms.BooleanField()
    bSortable_1 = forms.BooleanField()
    bSortable_2 = forms.BooleanField()
    bSortable_3 = forms.BooleanField()
    bSortable_4 = forms.BooleanField()
    bSortable_5 = forms.BooleanField()
    bSortable_6 = forms.BooleanField()
    bSortable_7 = forms.BooleanField()
    bSortable_8 = forms.BooleanField()
    iColumns = forms.IntegerField()
    iDisplayLength = forms.IntegerField()
    iDisplayStart = forms.IntegerField()
    iSortCol_0 = forms.IntegerField()
    iSortingCols = forms.IntegerField()
    mDataProp_0 = forms.IntegerField()
    mDataProp_1 = forms.IntegerField()
    mDataProp_2 = forms.IntegerField()
    mDataProp_3 = forms.IntegerField()
    mDataProp_4 = forms.IntegerField()
    mDataProp_5 = forms.IntegerField()
    mDataProp_6 = forms.IntegerField()
    mDataProp_7 = forms.IntegerField()
    mDataProp_8 = forms.IntegerField()
    sColumns = forms.CharField(required=False)
    sEcho = forms.IntegerField()
    sSearch = forms.CharField(required=False)
    sSearch_0 = forms.CharField(required=False)
    sSearch_1 = forms.CharField(required=False)
    sSearch_2 = forms.CharField(required=False)
    sSearch_3 = forms.CharField(required=False)
    sSearch_4 = forms.CharField(required=False)
    sSearch_5 = forms.CharField(required=False)
    sSearch_6 = forms.CharField(required=False)
    sSearch_7 = forms.CharField(required=False)
    sSearch_8 = forms.CharField(required=False)
    sSortDir_0 = forms.ChoiceField(choices=(('asc', 'asc'), ('desc', 'desc')))
