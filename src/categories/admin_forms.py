from django import forms

from documents.fields import MetadataTypeChoiceField
from .models import CategoryTemplate


class CategoryTemplateAdminForm(forms.ModelForm):
    """Custom form for category template. For admin use only."""
    metadata_model = MetadataTypeChoiceField()

    class Meta:
        model = CategoryTemplate
        fields = ('name', 'slug', 'description', 'use_creation_form',
                  'display_reporting', 'metadata_model')
