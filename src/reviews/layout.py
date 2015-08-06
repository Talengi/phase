from django.template.loader import render_to_string
from django.template import Context
from crispy_forms.layout import LayoutObject


class ReviewsLayout(LayoutObject):
    template = 'layout/reviews_table.html'

    def render(self, form, form_style, context, template_pack=None):
        revision = form.instance
        reviews = form.reviews
        can_discuss = form.can_discuss

        return render_to_string(
            self.template,
            Context({
                'document': revision.document,
                'revision': revision,
                'reviews': reviews,
                'form_style': form_style,
                'can_discuss': can_discuss,
            }))
