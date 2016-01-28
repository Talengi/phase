# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.text import slugify

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


class SameCategoryRelatedDocument(object):
    """Form mixin used to limit related documents choices to those belonging to
     the same category."""
    def __init__(self, *args, **kwargs):
        super(SameCategoryRelatedDocument, self).__init__(*args, **kwargs)
        if 'related_documents' in self.fields:
            qs = self.category.documents.all()
            self.fields['related_documents'].queryset = qs


class GenericBaseDocumentForm(forms.ModelForm):
    """Base form used for transmittals. Transmittals need to handle
    related documents in différent catégories """
    def __init__(self, *args, **kwargs):
        self.read_only = kwargs.pop('read_only', False)
        self.request = kwargs.pop('request', None)
        self.category = kwargs.pop('category')
        super(GenericBaseDocumentForm, self).__init__(*args, **kwargs)
        self.prepare_form(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
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

    def clean(self):
        """Validate the document number and key."""
        data = super(GenericBaseDocumentForm, self).clean()

        # In the creation form, we display a single field: the document number.
        # The document_key must be generated from it.
        # But in other cases (e.g the import module) we directly submit the
        # document_key. In that case, we must copy the key to have a valid
        # document number. Project History is the reason this is so complicated.
        # See ticket #145 for more details.
        if 'document_number' in data and 'document_key' in data:
            if data['document_key'] and not data['document_number']:
                data['document_number'] = data['document_key']
            elif data['document_number']:
                data['document_key'] = slugify(data['document_number']).upper()

        return data


class BaseDocumentForm(SameCategoryRelatedDocument, GenericBaseDocumentForm):
    """Base document form used for any document excepted transmittals.
    These documents must handle related documents belonging to the same
    category. We keep this name to avoid breaking imports from customized
    models."""
    pass
