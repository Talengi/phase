# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from dashboards.forms import classpath


class DashboardSelect(forms.Select):
    def render(self, name, value, attrs=None, choices=()):
        value = classpath(value)
        return super(DashboardSelect, self).render(
            name, value, attrs, choices)
