from django import forms

from documents.models import Document


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
