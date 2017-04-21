import operator

from django.template.loader import render_to_string
from crispy_forms.layout import LayoutObject


class ReviewsLayout(LayoutObject):
    template = 'layout/reviews_table.html'

    def render(self, form, form_style, context, template_pack=None):
        revision = form.instance
        reviews = form.reviews
        # We need to have the list sorted by role and by insertion order
        # for reviewsers. We sort the review list in two steps, (python lists
        # retains their original order). First we sort items according to their
        #  pk, then according to the role name in order to get Reviewers,
        # then the Leader and finally The Approver (R, L, A)
        reviews.sort(key=operator.attrgetter('pk'))
        reviews.sort(key=operator.attrgetter('role'), reverse=True)
        nb_comments = form.nb_comments
        can_discuss = form.can_discuss

        return render_to_string(self.template, {
            'document': revision.document,
            'revision': revision,
            'reviews': reviews,
            'nb_comments': nb_comments,
            'form_style': form_style,
            'can_discuss': can_discuss,
        })


class QuickDistributionListWidgetLayout(LayoutObject):
    template = 'layout/distribution_list_widget.html'

    def render(self, form, *args, **kwargs):
        return render_to_string(self.template, {
            'category': form.category
        })
