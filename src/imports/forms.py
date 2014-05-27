from django import forms

from documents.fields import MetadataTypeChoiceField
from imports.models import ImportBatch


class FileUploadForm(forms.ModelForm):
    imported_type = MetadataTypeChoiceField()

    class Meta:
        model = ImportBatch
        fields = ('imported_type', 'file')
