from django import forms
from django.utils.translation import ugettext_lazy as _

from categories.models import Category
from imports.models import ImportBatch


class FileUploadForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        label=_('Category'),
        required=True,
        queryset=Category.objects.select_related('organisation', 'category_template')
    )

    class Meta:
        model = ImportBatch
        fields = ('category', 'file')
