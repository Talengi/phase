# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.contenttypes.models import ContentType

from documents.fileutils import revision_file_path

from privatemedia.fields import PrivateFileField


class RevisionFileField(PrivateFileField):
    """Custom file field to store revision files."""

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'upload_to': revision_file_path,
        })
        return super(RevisionFileField, self).__init__(*args, **kwargs)


class MetadataTypeChoiceField(forms.ModelChoiceField):
    """A custom model choice field limited to document classes."""
    def __init__(self, *args, **kwargs):

        # We will set our own queryset, so user should not pass one
        qs = kwargs.pop('queryset', None)
        if qs:
            raise ValueError("We don't need a queryset, thank you")

        queryset = ContentType.objects \
            .filter(app_label__endswith='_documents') \
            .exclude(model__icontains='revision')
        kwargs.update({'queryset': queryset})

        super(MetadataTypeChoiceField, self).__init__(*args, **kwargs)
