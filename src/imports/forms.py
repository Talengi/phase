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


class CsvTemplateGenerationForm(forms.Form):
    category = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(CsvTemplateGenerationForm, self).__init__(*args, **kwargs)
        # We only want categories whose metadata model has `import_fields`
        # configured
        choices = [(c.pk, c) for c in Category.objects.all() if hasattr(
            c.category_template.metadata_model.model_class().PhaseConfig,
            'import_fields')]
        self.fields['category'].choices = choices

    class Meta:
        fields = ('category',)
