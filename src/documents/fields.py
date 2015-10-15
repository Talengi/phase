# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from documents.fileutils import revision_file_path
from documents.utils import get_all_document_qs

from privatemedia.fields import PrivateFileField


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


class MetadataTypeChoiceField(forms.ModelChoiceField):
    """A custom model choice field limited to document classes."""
    def __init__(self, *args, **kwargs):

        # We will set our own queryset, so user should not pass one
        qs = kwargs.pop('queryset', None)
        if qs:
            raise ValueError("We don't need a queryset, thank you")

        kwargs.update({'queryset': get_all_document_qs()})

        super(MetadataTypeChoiceField, self).__init__(*args, **kwargs)
