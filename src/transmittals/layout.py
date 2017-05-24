# -*- coding: utf-8 -*-


from django.template.loader import render_to_string

from crispy_forms.layout import LayoutObject


class RelatedRevisionsLayout(LayoutObject):
    template = 'transmittals/layout/related_revisions.html'

    def __init__(self, field):
        self.field = field

    def render(self, form, form_style, context, template_pack=None):
        revisions = form.instance.get_last_revisions()
        return render_to_string(self.template, {
            'revisions': revisions,
            'form_style': form_style,
        })


class OutgoingTrsLayout(LayoutObject):
    template = 'layout/outgoing_trs.html'

    def render(self, form, form_style, context, template_pack=None):
        transmittals = form.instance.transmittals.all()
        return render_to_string(self.template, {
            'transmittals': transmittals,
            'form_style': form_style,
        })
