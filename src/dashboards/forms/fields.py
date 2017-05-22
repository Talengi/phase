# -*- coding: utf-8 -*-


from django import forms

from dashboards.forms import classpath
from dashboards.forms.widgets import DashboardSelect
from django.utils.encoding import force_text


class DashboardTypeChoiceField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = DashboardSelect
        super(DashboardTypeChoiceField, self).__init__(*args, **kwargs)

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        choices = list(value)
        self._choices = choices

        text_choices = [(
            classpath(subclass) if subclass else subclass,
            name
        ) for subclass, name in choices]

        self.widget.choices = text_choices

    choices = property(_get_choices, _set_choices)

    def valid_value(self, value):
        text_value = force_text(value)
        for k, v in self.choices:
            if isinstance(k, type):
                k = classpath(k)
            if value == k or text_value == force_text(k):
                return True
        return False

    def prepare_value(self, value):
        """Fix prepared value.

        The `BoundField` class automatically instanciates values when they
        are callable, which we don't want, so we have to reverse this
        action here.

        See `django.forms.forms.BoundField.value`

        """
        if not isinstance(value, type):
            value = value.__class__
        return value
