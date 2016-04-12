# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _

from braces.views import LoginRequiredMixin

from categories.views import CategoryMixin


class AlertList(LoginRequiredMixin, CategoryMixin, TemplateView):
    template_name = 'alerts/alert_list.html'

    def breadcrumb_section(self):
        return (_('Alerts'), '#')


class AlertNewDocument(TemplateView):
    pass
