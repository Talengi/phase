# -*- coding: utf-8 -*-


from django.template.loader import render_to_string

from crispy_forms.layout import LayoutObject


class RelatedRevisionsLayout(LayoutObject):
    template = 'transmittals/layout/related_revisions.html'

    def __init__(self, field):
        self.field = field

    def render(self, form, form_style, context, template_pack=None):
        revisions = form.instance.get_revisions()
        return render_to_string(self.template, {
            'revisions': revisions,
            'form_style': form_style,
            'category': form.instance.document.category,
            'organisation': form.instance.document.category.organisation,
            'transmittal_number': form.instance.document.document_key,
            'user': context['user'],
        })


class OutgoingTrsLayout(LayoutObject):
    template = 'layout/outgoing_trs.html'

    def render(self, form, form_style, context, template_pack=None):
        transmittals = form.instance.transmittals \
            .select_related('document')
        return render_to_string(self.template, {
            'revision': form.instance,
            'transmittals': transmittals,
            'form_style': form_style,
        })
