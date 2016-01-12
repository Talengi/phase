# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.loader import render_to_string
from django.template import Context

from crispy_forms.layout import LayoutObject


class RelatedRevisionsLayout(LayoutObject):
    template = 'transmittals/layout/related_revisions.html'

    def __init__(self, field):
        self.field = field

    def render(self, form, form_style, context, template_pack=None):
        revisions = form.instance.get_revisions()

        return render_to_string(
            self.template,
            Context({
                'revisions': revisions,
                'form_style': form_style,
            }))


class OutgoingTrsLayout(LayoutObject):
    template = 'layout/outgoing_trs.html'

    def render(self, form, form_style, context, template_pack=None):
        transmittal = form.instance.transmittal

        return render_to_string(
            self.template,
            Context({
                'transmittal': transmittal,
                'form_style': form_style,
            }))
