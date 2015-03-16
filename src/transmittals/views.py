# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import TemplateView, ListView
from django.utils.translation import ugettext_lazy as _
from braces.views import LoginRequiredMixin


class TransmittalListView(LoginRequiredMixin, ListView):
    context_object_name = 'transmittal_list'

    def breadcrumb_section(self):
        return _('Transmittals')

    def get_queryset(self):
        from transmittals.models import Transmittal
        # TODO
        # - Does anyone has the right to view every transmittals?
        # - Configure ACLs
        return Transmittal.objects.all()


class TransmittalDiffView(TemplateView):
    template_name = 'transmittals/diff_view.html'

    def breadcrumb_section(self):
        return 'Transmittal'

    def breadcrumb_subsection(self):
        return 'FAC10005-CTR-CLT-TRS-00001'


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
