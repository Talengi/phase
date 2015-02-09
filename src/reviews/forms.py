# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from reviews.utils import get_cached_reviews
from accounts.fields import UserChoiceField, UserMultipleChoiceField


class ReviewFormMixin(forms.ModelForm):
    leader = UserChoiceField(
        label=_('Leader'),
        required=False,
        help_text=_('The leader is required to start the review'))
    approver = UserChoiceField(label=_('Approver'), required=False)
    reviewers = UserMultipleChoiceField(label=_('Reviewers'), required=False)

    def prepare_form(self, *args, **kwargs):
        if self.instance.id:
            self.reviews = get_cached_reviews(self.instance)
        super(ReviewFormMixin, self).prepare_form(*args, **kwargs)
