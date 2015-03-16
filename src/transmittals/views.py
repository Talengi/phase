# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import TemplateView, ListView, DetailView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin

from transmittals.models import Transmittal


class TransmittalListView(LoginRequiredMixin, ListView):
    context_object_name = 'transmittal_list'

    def breadcrumb_section(self):
        return (_('Transmittals'), reverse('transmittal_list'))

    def get_queryset(self):
        # TODO
        # - Does anyone has the right to view every transmittals?
        # - Configure ACLs
        return Transmittal.objects.all()


class TransmittalDiffView(LoginRequiredMixin, DetailView):
    template_name = 'transmittals/diff_view.html'
    context_object_name = 'transmittal'
    model = Transmittal
    slug_field = 'transmittal_key'
    slug_url_kwarg = 'transmittal_key'

    def breadcrumb_section(self):
        return (_('Transmittals'), reverse('transmittal_list'))

    def breadcrumb_object(self):
        return self.object


class DemoDiffView(TemplateView):
    template_name = 'transmittals/diff_view.html'

    def breadcrumb_section(self):
        return 'Transmittal'

    def breadcrumb_subsection(self):
        return 'FAC10005-CTR-CLT-TRS-00001'


class DemoRevisionDiffView(TemplateView):
    template_name = 'transmittals/revision_diff_view.html'

    def breadcrumb_section(self):
        return 'Transmittal'

    def breadcrumb_subsection(self):
        return 'FAC10005-CTR-CLT-TRS-00001'
