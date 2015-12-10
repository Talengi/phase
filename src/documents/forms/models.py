# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from crispy_forms.helper import FormHelper
from default_documents.layout import DocumentFieldset, FlatRelatedDocumentsLayout
from metadata.fields import ConfigurableChoiceField

from django.conf import settings


def documentform_factory(model):
    """Gets the given model edition form.

    We are looking for the form class in all installed apps.

    """
    form_class_name = '%sForm' % model.__name__
    apps = settings.INSTALLED_APPS
    DocumentForm = None

    for app in apps:
        form_path = '{}.forms.{}'.format(
            app, form_class_name)
        try:
            DocumentForm = import_string(form_path)
            break
        except (ImportError, AttributeError):
            continue

    else:
        raise ImproperlyConfigured('Cannot find class %s' % form_class_name)

    return DocumentForm


class BaseDocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.read_only = kwargs.pop('read_only', False)
        self.request = kwargs.pop('request', None)
        self.category = kwargs.pop('category')
        super(BaseDocumentForm, self).__init__(*args, **kwargs)
        self.prepare_form(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = self.build_layout()

        # Document key is automatically generated, this field should not be required
        if 'document_number' in self.fields:
            self.fields['document_number'].required = False

    def build_layout(self):
        raise NotImplementedError('Missing "build_layout" method')

    def prepare_form(self, *args, **kwargs):
        """Perform some common operations."""

        # Initialize values lists choices
        # See metadata.fields.ConfigurableChoiceField
        for field_name, field in self.fields.items():
            model_field = self._meta.model._meta.get_field(field_name)
            if isinstance(model_field, ConfigurableChoiceField):
                self.fields[field_name].choices = model_field.get_choices()

    def get_related_documents_layout(self):
        # Init related documents field
        if 'related_documents' in self.fields:
            if self.read_only:
                related_documents = DocumentFieldset(
                    _('Related documents'),
                    FlatRelatedDocumentsLayout('related_documents'),
                )
            else:
                related_documents = DocumentFieldset(
                    _('Related documents'),
                    'related_documents',
                )
        return related_documents

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
