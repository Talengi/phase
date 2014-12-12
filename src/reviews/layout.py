from django.template.loader import render_to_string
from django.template import Context
from crispy_forms.layout import LayoutObject


class ReviewsLayout(LayoutObject):
    template = 'layout/reviews_table.html'

    def render(self, form, form_style, context, template_pack=None):
        revision = form.instance
        reviews = form.reviews

        return render_to_string(
            self.template,
            Context({
                'document': revision.document,
                'revision': revision,
                'reviews': reviews,
                'form_style': form_style,
            }))
