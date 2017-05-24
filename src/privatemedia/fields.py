# -*- coding: utf-8 -*-


from django.db import models
from django.forms import fields

from privatemedia.storage import protected_storage, private_storage
from privatemedia.widgets import PhaseClearableFileInput


class BaseFileField(models.FileField):
    """Store files in a private dir."""
    def formfield(self, **kwargs):
        defaults = {
            'form_class': PhaseClearableFileField,
            'max_length': self.max_length,
        }
        if 'initial' in kwargs:
            defaults['required'] = False
        defaults.update(kwargs)
        return super(BaseFileField, self).formfield(**defaults)


class ProtectedFileField(BaseFileField):
    """Store files in a private dir."""
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'storage': protected_storage,
        })
        return super(ProtectedFileField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ProtectedFileField, self).deconstruct()
        kwargs['storage'] = protected_storage
        return name, path, args, kwargs


class PrivateFileField(BaseFileField):
    """Store files in a private dir."""
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'storage': private_storage,
        })
        return super(PrivateFileField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(PrivateFileField, self).deconstruct()
        kwargs['storage'] = protected_storage
        return name, path, args, kwargs


class PhaseClearableFileField(fields.FileField):
    widget = PhaseClearableFileInput
