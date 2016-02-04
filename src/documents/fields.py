# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms import fields
from django.db.utils import ProgrammingError

from documents.fileutils import revision_file_path
from documents.utils import get_all_document_qs

from privatemedia.fields import PrivateFileField
from documents.widgets import RevisionClearableFileInput


class RevisionFileField(PrivateFileField):
    """Custom file field to store revision files."""

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': revision_file_path,
        })
        return super(RevisionFileField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(RevisionFileField, self).deconstruct()
        kwargs['upload_to'] = revision_file_path
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'form_class': RevisionClearableFileField,
        }
        defaults.update(kwargs)
        return super(RevisionFileField, self).formfield(**defaults)


class RevisionClearableFileField(fields.FileField):
    widget = RevisionClearableFileInput


class MetadataTypeChoiceField(forms.ModelChoiceField):
    """A custom model choice field limited to document classes."""
    def __init__(self, *args, **kwargs):

        # We will set our own queryset, so user should not pass one
        qs = kwargs.pop('queryset', None)
        if qs:
            raise ValueError("We don't need a queryset, thank you")

        try:
            qs = get_all_document_qs()
        except ProgrammingError:
            # This will happen when rebuilding db from schatch, e.g
            # when running tests, and can be ignored safely
            qs = []
        kwargs.update({'queryset': qs})

        super(MetadataTypeChoiceField, self).__init__(*args, **kwargs)
