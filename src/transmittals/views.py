# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import TemplateView, ListView, DetailView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import Http404
from braces.views import LoginRequiredMixin

from transmittals.models import Transmittal, TrsRevision


class TransmittalListView(LoginRequiredMixin, ListView):
    """List all transmittals."""
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

    def get_context_data(self, **kwargs):
        context = super(TransmittalDiffView, self).get_context_data(**kwargs)
        context.update({
            'revisions': self.object.trsrevision_set.all()
        })

        return context


class TransmittalRevisionDiffView(LoginRequiredMixin, DetailView):
    template_name = 'transmittals/revision_diff_view.html'
    context_object_name = 'trs_revision'

    def breadcrumb_section(self):
        return (_('Transmittals'), reverse('transmittal_list'))

    def breadcrumb_subsection(self):
        return self.object.transmittal

    def breadcrumb_object(self):
        return self.object

    def get_object(self, queryset=None):
        qs = TrsRevision.objects \
            .filter(transmittal__transmittal_key=self.kwargs['transmittal_key']) \
            .filter(document_key=self.kwargs['document_key']) \
            .filter(revision=self.kwargs['revision']) \
            .select_related('transmittal', 'document')
        try:
            obj = qs.get()
        except(qs.model.DoesNotExist):
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': qs.model._meta.verbose_name})

        return obj


class DemoDiffView(TemplateView):
    template_name = 'transmittals/demo_diff_view.html'

    def breadcrumb_section(self):
        return 'Transmittal'

    def breadcrumb_subsection(self):
        return 'FAC10005-CTR-CLT-TRS-00001'


class DemoRevisionDiffView(TemplateView):
    template_name = 'transmittals/demo_revision_diff_view.html'

    def breadcrumb_section(self):
        return 'Transmittal'

    def breadcrumb_subsection(self):
        return 'FAC10005-CTR-CLT-TRS-00001'
