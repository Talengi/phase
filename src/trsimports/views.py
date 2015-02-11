# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import TemplateView


class DiffView(TemplateView):
    template_name = 'transmittals/diff_view.html'

    def breadcrumb_section(self):
        return 'Transmittal'

    def breadcrumb_subsection(self):
        return 'FAC10005-CTR-CLT-TRS-00001'


class RevisionDiffView(TemplateView):
    template_name = 'transmittals/revision_diff_view.html'
