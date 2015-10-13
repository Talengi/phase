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
        """Validate the reviewers

        During review, reviewers can only be modified during the reviewers step.
        A reviewer that posted a review cannot be deleted anymore.

        """
        reviewers = self.cleaned_data['reviewers']
        if not self.instance.is_under_review():
            return reviewers

        old_reviewers = self.instance.reviewers.all()

        # Reviewers were modified
        if set(reviewers) != set(old_reviewers):

            # If reviewers step is finished, reviewers cannot be modified anymore
            if self.instance.reviewers_step_closed:
                error = _('Reviewers step is over, you cannot modify reviewers anymore')
                raise ValidationError(error, code='reviewers')

            # if some reviewers were deleted, check that none of the them
            # actually submitted a review
            deleted_reviewers = set(old_reviewers) - set(reviewers)
            deleted_reviews_with_comments = self.instance.get_filtered_reviews(
                lambda rev: rev.reviewer in deleted_reviewers and
                rev.status != 'progress')
            if len(deleted_reviews_with_comments) > 0:
                errors = []
                for review in deleted_reviews_with_comments:
                    errors.append(ValidationError(
                        _('%(user)s already submitted a review, and cannot be '
                          'removed from the distribution list.'),
                        code='reviewers',
                        params={'user': review.reviewer}))
                raise ValidationError(errors, code='reviewers')

        return reviewers

    def clean_leader(self):
        leader = self.cleaned_data['leader']
        if not self.instance.is_under_review():
            return leader

        # If leader step is over, leader cannot be changed anymore
        if self.instance.leader_step_closed:
            if leader != self.instance.leader:
                error = _('Leader stop is over, you cannot modify leader anymore.')
                raise ValidationError(error, code='leader')

        return leader

    def clean_approver(self):
        approver = self.cleaned_data['approver']
        if not self.instance.is_under_review():
            return approver

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
