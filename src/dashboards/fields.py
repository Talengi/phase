# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from importlib import import_module

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.six import with_metaclass, string_types
from django.utils.module_loading import import_string
from django.conf import settings

from dashboards.forms.fields import DashboardTypeChoiceField
from dashboards.dashboards import DashboardProvider


def classpath(klass):
    return '{}.{}'.format(
        klass.__module__, klass.__name__)


class DashboardProviderChoiceField(with_metaclass(models.SubfieldBase, models.Field)):
    """Custom model field to select a `DashboardProvider` subclass."""

    description = "Field to select a DashboardProvider subclass."

    def get_internal_type(self):
        return "CharField"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 250)
        super(DashboardProviderChoiceField, self).__init__(*args, **kwargs)
        self._choices = None

    def _get_choices(self, *args, **kwargs):
        if self._choices is None:
            self._choices = self._get_all_dashboard_providers()
        return self._choices
    choices = property(_get_choices)

    def _get_all_dashboard_providers(self):
        """Return the list of all available dashboard providers.

        Copied from django admin's autodiscover.

        """
        from dashboards.dashboards import DashboardProvider

        for app in settings.INSTALLED_APPS:
            try:
                import_module('{}.dashboards'.format(app))
            except:
                pass

        providers = []
        for subclass in DashboardProvider.__subclasses__():
            providers.append((
                subclass,
                subclass.__name__
            ))
        return providers

    def to_python(self, value):
        """Converts the stored string to a python type."""
        if value == '':
            return None

        if isinstance(value, string_types):
            try:
                value = import_string(value)
            except:
                raise ValidationError('The class {} does not exist'.format(
                    value))

        if not isinstance(value, type):
            raise ValidationError('This should be a python class.')

        if not issubclass(value, DashboardProvider):
            raise ValidationError('This is not a valid Dashboard provider class')

        return value

    def get_prep_value(self, value):
        """Converts type to string."""
        return classpath(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'choices_form_class': DashboardTypeChoiceField}
        defaults.update(kwargs)
        return super(DashboardProviderChoiceField, self).formfield(**defaults)
