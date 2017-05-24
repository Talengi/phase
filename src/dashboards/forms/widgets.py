# -*- coding: utf-8 -*-


from django import forms

from dashboards.forms import classpath


class DashboardSelect(forms.Select):
    def get_context(self, name, value, attrs):
        value = classpath(value)
        context = super(DashboardSelect, self).get_context(name, value, attrs)
        return context
