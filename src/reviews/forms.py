# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from crispy_forms.layout import Field

from accounts.forms import UserChoiceField, UserMultipleChoiceField
from default_documents.layout import (
    DocumentFieldset, PropertyLayout, YesNoLayout, DateField)
from reviews.utils import get_cached_reviews
from reviews.layout import ReviewsLayout
from reviews.models import Review


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

            # Extract non null comments from reviews
            all_comments = map(lambda x: x.comments or None, self.reviews)
            comments = filter(lambda x: x, all_comments)
            self.nb_comments = len(comments)

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
        if self.instance.review_start_date is None:
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
        if self.instance.review_start_date is None:
            return leader

        # If leader step is over, leader cannot be changed anymore
        if self.instance.leader_step_closed:
            if leader != self.instance.leader:
                error = _('Leader stop is over, you cannot modify leader anymore.')
                raise ValidationError(error, code='leader')

        return leader

    def clean_approver(self):
        approver = self.cleaned_data['approver']
        if self.instance.review_start_date is None:
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
        distrib_list = []

        leader = data.get('leader', None)
        if leader:
            distrib_list.append(leader)

        approver = data.get('approver', None)
        if approver:
            distrib_list.append(approver)

        reviewers = data.get('reviewers', [])
        distrib_list += reviewers

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

    def get_review_layout(self):
        """Get layout for the form "Review" section."""
        if self.read_only:
            review_layout = (
                DocumentFieldset(
                    _('Review'),
                    DateField('received_date'),
                    PropertyLayout('return_code'),
                    Field('review_start_date', readonly='readonly'),
                    Field('review_due_date', readonly='readonly'),
                    PropertyLayout('get_current_review_step_display'),
                    YesNoLayout('is_under_review'),
                    YesNoLayout('is_overdue'),
                    'trs_return_code',
                    'trs_comments'),
                DocumentFieldset(
                    _('Distribution list'),
                    ReviewsLayout()))
        else:
            review_layout = (
                DocumentFieldset(
                    _('Review'),
                    DateField('received_date'),
                    PropertyLayout('return_code'),
                    Field('review_start_date', readonly='readonly'),
                    Field('review_due_date', readonly='readonly'),
                    PropertyLayout('get_current_review_step_display'),
                    YesNoLayout('is_under_review'),
                    YesNoLayout('is_overdue'),
                    'trs_return_code',
                    'trs_comments',
                    'reviewers',
                    'leader',
                    'approver'),)

        return review_layout


class BasePostReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('comments', 'return_code')

    def clean_return_code(self):
        """Validate the return code field.

        If the user is a simple reviewer, this field is not in the form
        so this validation method is not executed.

        If the user is leader or approver, we need to make sure the return
        code was present in the form BUT we must not raise an error if the
        form was submitted without posting a review, e.g clicking on the
        "cancel X step" or "send back to leader" buttons.

        """
        return_code = self.cleaned_data['return_code']
        empty_values = self.fields['return_code'].empty_values

        # The user tried to submit a review without a return code
        if return_code in empty_values and 'review' in self.data:
            raise forms.ValidationError('This field is required.')

        return return_code
