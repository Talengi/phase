from django.template.loader import render_to_string
from django.template import Context
from crispy_forms.layout import LayoutObject

from reviews.models import Review


class ReviewsLayout(LayoutObject):
    template = 'layout/reviews_table.html'

    def render(self, form, form_style, context, template_pack=None):
        revision = form.instance
        reviews = Review.objects \
            .filter(document=revision.document) \
            .filter(revision=revision.revision) \
            .order_by('id') \
            .select_related('reviewer')

        return render_to_string(
            self.template,
            Context({
                'document': revision.document,
                'revision': revision,
                'reviews': reviews,
                'form_style': form_style,
            }))
