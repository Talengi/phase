# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from reviews.utils import get_cached_reviews
from accounts.fields import UserChoiceField, UserMultipleChoiceField


class ReviewFormMixin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReviewFormMixin, self).__init__(*args, **kwargs)

        # We declare those fields in __init__ because
        # we need to pass the `category` attribute, which we
        # only have at the form instantiation
        self.fields['leader'] = UserChoiceField(
            category=self.category,
            label=_('Leader'),
            required=False,
            help_text=_('The leader is required to start the review'))

        self.fields['approver'] = UserChoiceField(
            category=self.category,
            label=_('Approver'),
            required=False)

        self.fields['reviewers'] = UserMultipleChoiceField(
            category=self.category,
            label=_('Reviewers'),
            required=False)

    def prepare_form(self, *args, **kwargs):
        if self.instance.id:
            self.reviews = get_cached_reviews(self.instance)

            # Is the current user a member of the distribution list?
            self.can_discuss = False
            if self.request:
                reviewers = [review.reviewer for review in self.reviews]
                self.can_discuss = self.request.user in reviewers

        super(ReviewFormMixin, self).prepare_form(*args, **kwargs)
