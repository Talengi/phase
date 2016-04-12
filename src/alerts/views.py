# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView, ListView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from braces.views import LoginRequiredMixin

from documents.models import Document
from categories.views import CategoryMixin


class BaseAlert(LoginRequiredMixin, CategoryMixin):
    def breadcrumb_section(self):
        return (_('Alerts'), '#')

    def breadcrumb_subsection(self):
        return self.category


class AlertHome(BaseAlert, TemplateView):
    """Simply links to available alerts."""
    template_name = 'alerts/alert_home.html'


class BaseAlertList(BaseAlert, ListView):
    def get_context_data(self, **kwargs):
        context = super(BaseAlert, self).get_context_data(**kwargs)
        context.update({
            'alerts': self.get_alerts(context['object_list']),
        })
        return context

    def get_alerts(self, qs):
        return map(self.get_alert, qs)

    def get_alert(self, obj):
        return {
            'title': self.get_alert_title(obj),
            'description': self.get_alert_description(obj),
            'link': self.get_alert_link(obj),
            'pubdate': self.get_alert_pubdate(obj)
        }

    def get_alert_title(self, obj):
        return obj.title

    def get_alert_description(self, obj):
        return ''

    def get_alert_link(self, obj):
        return obj.get_absolute_url()

    def get_alert_pubdate(self, obj):
        return obj.created_on


class AlertNewDocument(BaseAlertList):
    """List newly created documents."""
    template_name = 'alerts/alert_new_document.html'
    context_object_name = 'alerts'

    def breadcrumb_objet(self):
        return (_('New document'), reverse('alert_new_document'))

    def get_queryset(self):
        qs = Document.objects \
            .filter(category=self.category) \
            .order_by('-created_on')[:settings.ALERT_ELEMENTS]
        return qs

    def get_alert_title(self, obj):
        return 'New document: {}'.format(obj.title)
