# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from reviews.utils import get_cached_reviews
from accounts.forms import UserChoiceField, UserMultipleChoiceField


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

    def clean_reviewers(self):
        reviewers = self.cleaned_data['reviewers']

        # If reviewers step is finished, reviewers cannot be modifies anymore
        if self.instance.reviewers_step_closed:
            old_reviewers = self.instance.reviewers.all()
            if set(reviewers) != set(old_reviewers):
                error = _('Reviewers step is over, you cannot modify reviewers anymore')
                raise ValidationError(error, code='reviewers')

        return reviewers

    def clean_leader(self):
        leader = self.cleaned_data['leader']

        # If leader step is over, leader cannot be changed anymore
        if self.instance.leader_step_closed:
            if leader != self.instance.leader:
                error = _('Leader stop is over, you cannot modify leader anymore.')
                raise ValidationError(error, code='leader')

        return leader

    def clean_approver(self):
        approver = self.cleaned_data['approver']

        # If approver step is over, leader cannot be changed anymore
        if self.instance.review_end_date:
            if approver != self.instance.approver:
                error = _('Approver stop is over, you cannot modify approver anymore.')
                raise ValidationError(error, code='approver')

        return approver

    def clean(self):
        data = super(ReviewFormMixin, self).clean()

        # Check that no user appears twice in the distrib list
        keys = ('reviewers', 'leader', 'approver')
        if not any(key in data for key in keys):
            distrib_list = []
            if data['leader'] is not None:
                distrib_list.append(data['leader'])

            if data['approver'] is not None:
                distrib_list.append(data['approver'])

            distrib_list += data['reviewers']

            distrib_set = set(distrib_list)
            if len(distrib_list) != len(distrib_set):
                msg = _('The same user cannot appear multiple times in the same '
                        'distribution list.')
                raise ValidationError(msg, code='duplicate_distrib_list')

        return data

    def save(self, commit=True):
        saved = super(ReviewFormMixin, self).save(commit)
        if saved.is_under_review():
            saved.sync_reviews()
        return saved
