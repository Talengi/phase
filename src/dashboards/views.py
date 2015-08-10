# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.views.generic import DetailView

from braces.views import LoginRequiredMixin

from dashboards.models import Dashboard


class DashboardView(LoginRequiredMixin, DetailView):
    template_name = 'dashboards/dashboard.html'
    model = Dashboard
    slug_url_kwarg = 'dashboard'
    context_object_name = 'dashboard'

    def breadcrumb_section(self):
        return self.object.category.organisation

    def breadcrumb_subsection(self):
        return 'Dashboards'

    def breadcrumb_object(self):
        return self.object

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        self.object.fetch_data()
        headers = self.object.get_headers()
        buckets = self.object.get_buckets()

        context.update({
            'dashboard_active': True,
            'headers': headers,
            'buckets': buckets,
        })

        return context
