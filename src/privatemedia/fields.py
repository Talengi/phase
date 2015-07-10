# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.forms import fields

from privatemedia.fileutils import private_storage
from privatemedia.widgets import PhaseClearableFileInput


class PrivateFileField(models.FileField):
    """Store files in a private dir."""
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'storage': private_storage,
        })
        return super(PrivateFileField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': PhaseClearableFileField,
            'max_length': self.max_length,
        }
        if 'initial' in kwargs:
            defaults['required'] = False
        defaults.update(kwargs)
        return super(PrivateFileField, self).formfield(**defaults)


class PhaseClearableFileField(fields.FileField):
    widget = PhaseClearableFileInput
