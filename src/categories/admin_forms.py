from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import CategoryTemplate


class CategoryTemplateAdminForm(forms.ModelForm):
    """Custom form for category template. For admin use only."""

    def __init__(self, *args, **kwargs):
        super(CategoryTemplateAdminForm, self).__init__(*args, **kwargs)

        # Define a custom queryset to limit the available
        # content types to actual Metadata models
        qs = ContentType.objects \
            .filter(app_label='documents')
        self.fields['metadata_model'].queryset = qs

    class Meta:
        model = CategoryTemplate
