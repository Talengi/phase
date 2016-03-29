# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from model_utils import Choices

from accounts.models import User
from documents.models import Document
from documents.templatetags.documents import MenuItem
from metadata.fields import ConfigurableChoiceField
from privatemedia.fields import PrivateFileField
from reviews.fileutils import review_comments_file_path

CLASSES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
)


class Review(models.Model):
    # Yes, two statuses with the same label.
    # See Trello#173
    STATUSES = Choices(
        ('void', ''),  # Only for dummy review in document form
        ('pending', _('Pending')),
        ('progress', _('In progress')),
        ('reviewed', _('Reviewed')),
        ('commented', _('Reviewed')),
        ('not_reviewed', _('Not reviewed')),
    )
    STEPS = Choices(
        ('pending', ''),
        ('reviewer', _('Reviewer')),
        ('leader', _('Leader')),
        ('approver', _('Approver')),
        ('closed', _('Closed')),
    )
    ROLES = Choices(
        ('reviewer', _('Reviewer')),
        ('leader', _('Leader')),
        ('approver', _('Approver')),
    )

    reviewer = models.ForeignKey(
        User,
        verbose_name=_('User'),
    )
    role = models.CharField(
        _('Role'),
        max_length=8,
        choices=ROLES,
        default=ROLES.reviewer
    )
    document = models.ForeignKey(
        Document,
        verbose_name=_('Document')
    )
    revision = models.PositiveIntegerField(
        _('Revision')
    )
    received_date = models.DateField(
        _('Review received date'),
        null=True, blank=True
    )
    start_date = models.DateField(
        _('Review start date'),
        null=True, blank=True
    )
    due_date = models.DateField(
        _('Review due date'),
        null=True, blank=True
    )
    docclass = models.IntegerField(
        verbose_name=u"Class",
        default=1,
        choices=CLASSES)
    status = models.CharField(
        _('Status'),
        max_length=30,
        choices=STATUSES,
        default=STATUSES.pending)
    revision_status = models.CharField(
        _('Revision status'),
        max_length=30,
        null=True, blank=True)
    closed_on = models.DateTimeField(
        _('Closed on'),
        null=True, blank=True)
    amended_on = models.DateTimeField(
        _('Amended on'),
        null=True, blank=True)
    comments = PrivateFileField(
        _('Comments'),
        null=True, blank=True,
        upload_to=review_comments_file_path
    )
    return_code = ConfigurableChoiceField(
        _('Return code'),
        max_length=3,
        null=True, blank=True,
        list_index='REVIEW_RETURN_CODES')

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        index_together = (('reviewer', 'document', 'revision', 'role'),)
        unique_together = ('reviewer', 'document', 'revision')
        app_label = 'reviews'

    def save(self, *args, **kwargs):
        cache_key = 'all_reviews_{}'.format(self.document_id)
        cache.delete(cache_key)
        super(Review, self).save(*args, **kwargs)

    @property
    def revision_name(self):
        return '%02d' % self.revision

    def post_review(self, comments, return_code=None, save=True):
        self.comments = comments
        self.return_code = return_code

        if self.closed_on is None:
            self.closed_on = timezone.now()
        else:
            self.amended_on = timezone.now()

        if comments:
            self.status = self.STATUSES.commented
        else:
            self.status = self.STATUSES.reviewed

        if save:
            self.save()

    def is_overdue(self):
        """Tells if the review is overdue.

        A review is overdue only if it's ongoing (ended reviews cannot
        be overdue) and the due date is past.

        """
        today = timezone.now().date()
        return self.due_date < today and self.closed_on is None

    def days_of_delay(self):
        """Gets the number of days between the due date and the review end.

        If the review has ended, returns delay between the due date and
        the completion date.

        If the review is ongoing, returns delay between the due date and the
        present day.

        """
        if self.closed_on:
            checked_date = self.closed_on
        else:
            checked_date = timezone.now().date()

        delta = checked_date - self.due_date
        return delta.days

    def get_comments_url(self):
        return reverse('download_review_comments', args=[
            self.document.document_key,
            self.revision,
            self.id
        ])


class ReviewMixin(models.Model):
    """A Mixin to use to define reviewable document types.
    The review duration is configurable via a tuple matching the CLASSES tuple.

    The duration is extracted.
    REVIEW_DURATIONS = (
        (1, 4),
        (2, 8),
        (3, 13),
        (4, 13),
    )
    e.g: if docclass field value is 2 then duration is 8, etc.
    """

    review_start_date = models.DateField(
        _('Review start date'),
        null=True, blank=True
    )
    review_due_date = models.DateField(
        _('Review due date'),
        null=True, blank=True
    )
    reviewers_step_closed = models.DateField(
        _('Reviewers step closed'),
        null=True, blank=True
    )
    leader_step_closed = models.DateField(
        _('Leader step closed'),
        null=True, blank=True
    )
    review_end_date = models.DateField(
        _('Review end date'),
        null=True, blank=True
    )
    reviewers = models.ManyToManyField(
        User,
        verbose_name=_('Reviewers'),
        blank=True)
    leader = models.ForeignKey(
        User,
        verbose_name=_('Leader'),
        related_name='%(app_label)s_%(class)s_related_leader',
        null=True, blank=True)
    approver = models.ForeignKey(
        User,
        verbose_name=_('Approver'),
        related_name='%(app_label)s_%(class)s_related_approver',
        null=True, blank=True)
    docclass = models.IntegerField(
        verbose_name=u"Class",
        default=1,
        choices=CLASSES)
    return_code = ConfigurableChoiceField(
        _('Return code'),
        max_length=3,
        null=True, blank=True,
        list_index='REVIEW_RETURN_CODES')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        cache_key = 'all_reviews_{}'.format(self.metadata.document_id)
        cache.delete(cache_key)
        super(ReviewMixin, self).save(*args, **kwargs)

    @cached_property
    def can_be_reviewed(self):
        """Is this revision ready to be reviewed.

        A revision can only be reviewed if at least a leader was defined.

        Also, a revision can only be reviewed once.

        """
        return all((
            self.received_date,
            self.leader_id,
            not self.review_start_date
        ))

    @transaction.atomic
    def start_review(self, at_date=None, due_date=None):
        """Starts the review process.

        This methods initiates the review process. We don't check whether the
        document can be reviewed or not, or if the process was already
        initiated. It's up to the developer to perform those checks before
        calling this method.

        """
        start_date = at_date or timezone.now()
        self.review_start_date = start_date

        duration = self.get_review_duration()
        self.review_due_date = due_date or \
            self.received_date + \
            datetime.timedelta(days=duration)

        reviewers = self.reviewers.all()
        for reviewer in reviewers:
            Review.objects.create(
                reviewer=reviewer,
                document=self.document,
                revision=self.revision,
                received_date=self.received_date,
                start_date=start_date,
                due_date=self.review_due_date,
                docclass=self.docclass,
                status='progress',
                revision_status=self.status)

        # If no reviewers, close reviewers step immediatly
        if len(reviewers) == 0:
            self.reviewers_step_closed = start_date
            leader_review_status = 'progress'
        else:
            leader_review_status = 'pending'

        # Leader is mandatory, no need to test it
        Review.objects.create(
            reviewer_id=self.leader_id,
            role=Review.ROLES.leader,
            document=self.document,
            revision=self.revision,
            received_date=self.received_date,
            start_date=start_date,
            due_date=self.review_due_date,
            status=leader_review_status,
            docclass=self.docclass,
            revision_status=self.status)

        # Approver is not mandatory
        if self.approver_id:
            Review.objects.create(
                reviewer_id=self.approver_id,
                role=Review.ROLES.approver,
                document=self.document,
                revision=self.revision,
                received_date=self.received_date,
                start_date=start_date,
                due_date=self.review_due_date,
                status=leader_review_status,
                docclass=self.docclass,
                revision_status=self.status)

        self.reload_reviews()
        self.save(update_document=True)

    @transaction.atomic
    def cancel_review(self):
        """Stops the review process.

        This methods reverts the "start_review" process. It simply deletes all
        data related to the current review, and leaves the document in the
        state it was before starting the review.

        This method can cause data loss.

        """
        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .delete()

        self.review_start_date = None
        self.review_due_date = None
        self.review_end_date = None
        self.reviewers_step_closed = None
        self.leader_step_closed = None
        self.save(update_document=True)

        from reviews.signals import review_canceled
        review_canceled.send(sender=self.__class__, instance=self)

    @transaction.atomic
    def end_reviewers_step(self, at_date=None, save=True):
        """Ends the first step of the review."""
        end_date = at_date or timezone.now()
        self.reviewers_step_closed = end_date

        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=Review.ROLES.reviewer) \
            .filter(closed_on=None) \
            .update(closed_on=end_date, status='not_reviewed')

        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=Review.ROLES.leader) \
            .update(status='progress')

        self.reload_reviews()
        if save:
            self.save(update_document=True)

    @transaction.atomic
    def end_leader_step(self, at_date=None, save=True):
        """Ends the second step of the review.

        Also ends the first step if it wasn't already done.

        """
        if self.reviewers_step_closed is None:
            self.end_reviewers_step(save=False, at_date=at_date)

        end_date = at_date or timezone.now()

        self.leader_step_closed = end_date

        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=Review.ROLES.leader) \
            .filter(closed_on=None) \
            .update(closed_on=end_date, status='not_reviewed')

        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=Review.ROLES.approver) \
            .update(status='progress')

        if not self.approver_id:
            self.review_end_date = end_date

        self.reload_reviews()
        if save:
            self.save(update_document=True)

    @transaction.atomic
    def send_back_to_leader_step(self, save=True):
        """Send the review back to the leader step."""
        self.leader_step_closed = None

        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=Review.ROLES.leader) \
            .update(closed_on=None, status='progress')

        self.reload_reviews()
        if save:
            self.save(update_document=True)

    @transaction.atomic
    def end_review(self, at_date=None, save=True):
        """Ends the review.

        Also ends the steps before.

        """
        if self.leader_step_closed is None:
            self.end_leader_step(save=False, at_date=at_date)

        end_date = at_date or timezone.now()
        self.review_end_date = end_date

        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=Review.ROLES.approver) \
            .filter(closed_on=None) \
            .update(closed_on=end_date, status='not_reviewed')

        self.reload_reviews()
        if save:
            self.save(update_document=True)

    @transaction.atomic
    def sync_reviews(self):
        """Update Review objects so it's coherent with current object state.

        If the distribution list (reviewers, leader, approver) was modified in
        the document form, the corresponding Review objects must be created /
        deleted to stay in sync.

        """
        # Sync leader
        leader_review = self.get_leader_review()
        if leader_review.reviewer_id != self.leader_id:
            leader_review.reviewer = self.leader
            leader_review.save()

        # Sync approver
        # Several cases here
        #  * an existing approver review was deleted
        #  * an existing approver review was modified
        #  * an approver review was created
        approver_review = self.get_approver_review()
        if approver_review:
            if approver_review.reviewer_id != self.approver_id:
                # A new approver was submitted
                if self.approver:
                    approver_review.reviewer = self.approver
                    approver_review.save()
                # The approver was deleted
                else:
                    approver_review.delete()
                    # If we were at the last review step, end the review completely
                    if self.is_at_review_step(Review.STEPS.approver):
                        self.end_review()
        else:
            if self.approver:
                Review.objects.create(
                    reviewer=self.approver,
                    role=Review.ROLES.approver,
                    document=self.document,
                    revision=self.revision,
                    received_date=self.received_date,
                    start_date=self.review_start_date,
                    due_date=self.review_due_date,
                    docclass=self.docclass,
                    status='pending',
                    revision_status=self.status)

        # Sync reviewers
        old_reviews = self.get_reviewers_reviews()
        old_reviewers = set(review.reviewer for review in old_reviews)
        current_reviewers = set(self.reviewers.all())

        # Create Review objects for new reviewers
        new_reviewers = current_reviewers - old_reviewers
        for reviewer in new_reviewers:
            Review.objects.create(
                reviewer=reviewer,
                document=self.document,
                revision=self.revision,
                received_date=self.received_date,
                start_date=self.review_start_date,
                due_date=self.review_due_date,
                docclass=self.docclass,
                status='progress',
                revision_status=self.status)

        # Remove Review objects for deleted reviewers
        deleted_reviewers = old_reviewers - current_reviewers
        if len(deleted_reviewers) > 0:
            for reviewer in deleted_reviewers:
                review = self.get_review(reviewer)
                # Check that we only delete review with no comments
                # This condition is enforced in the ReviewMixinForm anyway
                if review.status != 'progress':
                    raise RuntimeError('Cannot delete a review with comments')
                review.delete()

            # Should we end the reviewers step?
            waiting_reviews = self.get_filtered_reviews(
                lambda rev: rev.id and rev.role == 'reviewer' and
                rev.status == 'progress')
            if len(waiting_reviews) == 0:
                self.end_reviewers_step()

        self.reload_reviews()

    def is_under_review(self):
        """It's under review only if review has started but not ended."""
        return bool(self.review_start_date) != bool(self.review_end_date)

    is_under_review.short_description = _('Under review')

    def is_overdue(self):
        """Tells if the review is overdue.

        A review is overdue only if it's ongoing (ended reviews cannot
        be overdue) and the due date is past.

        """
        today = timezone.now().date()
        return self.is_under_review() and self.review_due_date < today

    is_overdue.short_description = _('Overdue')

    def current_review_step(self):
        """Return a string representing the current step."""
        if self.review_start_date is None:
            return Review.STEPS.pending

        if self.reviewers_step_closed is None:
            return Review.STEPS.reviewer

        if self.leader_step_closed is None:
            return Review.STEPS.leader

        if self.review_end_date is None:
            return Review.STEPS.approver

        return Review.STEPS.closed

    current_review_step.short_description = _('Current review step')

    def get_current_review_step_display(self):
        step = self.current_review_step()
        return dict(Review.STEPS)[step]

    get_current_review_step_display.short_description = _(
        'Current review step')

    def is_at_review_step(self, step):
        return step == self.current_review_step()

    def get_reviews(self):
        """Get all reviews associated with this revision."""
        if not hasattr(self, '_reviews'):
            qs = Review.objects \
                .filter(document=self.document) \
                .filter(revision=self.revision) \
                .order_by('id') \
                .select_related('reviewer')
            self._reviews = qs
        return self._reviews

    def reload_reviews(self):
        """Reload the review cache."""
        if hasattr(self, '_reviews'):
            del self._reviews

    def get_review_duration(self):
        """We can define `REVIEW_DURATIONS` tuple in class attributes. Then we
         return the duration matched by `docclass` field. If `REVIEW_DURATIONS`
          is not present, the global value `REVIEW_DURATION` is in settings."""

        # If REVIEW_DURATIONS is not defined we get the settings value
        if not hasattr(self, 'REVIEW_DURATIONS'):
            return settings.REVIEW_DURATION

        review_durations = dict(self.REVIEW_DURATIONS)

        # We try to get the duration from the tuple
        review_duration = review_durations.get(self.docclass, None)
        if review_duration is None:
            raise ImproperlyConfigured(
                'Define {0}.REVIEW_DURATIONS to match reviews.models.CLASSES'
                'or define settings.LOGIN_URL or '
                'override {0}.get_review_duration().'.format(
                    self.__class__.__name__))
        return review_duration

    def get_review(self, user):
        """Get the review from this specific user."""
        reviews = self.get_reviews()
        rev = next((rev for rev in reviews if rev.reviewer == user), None)
        return rev

    def get_filtered_reviews(self, filter):
        reviews = self.get_reviews()
        filtered = [rev for rev in reviews if filter(rev)]
        return filtered

    def get_reviewers_reviews(self):
        reviews = self.get_reviews()
        return [rev for rev in reviews if rev.role == 'reviewer']

    def get_leader_review(self):
        reviews = self.get_reviews()
        rev = next((rev for rev in reviews if rev.role == 'leader'), None)
        return rev

    def get_approver_review(self):
        reviews = self.get_reviews()
        rev = next((rev for rev in reviews if rev.role == 'approver'), None)
        return rev

    def is_reviewer(self, user):
        return user in self.reviewers.all()

    def get_initial_ignored_fields(self):
        ignored = (
            'review_start_date',
            'review_due_date',)
        return super(ReviewMixin, self).get_initial_ignored_fields() + ignored

    def get_new_revision_initial(self, form):
        initial = super(ReviewMixin, self).get_new_revision_initial(form)
        initial.update({
            'leader': self.leader_id,
            'approver': self.approver_id,
            'reviewers': self.reviewers.values_list('id', flat=True),
        })

        return initial

    def post_trs_import(self, trs_revision):
        """See `documents.models.MetadataRevision.post_trs_import`

        If we are importing a revision with review data, we need to make sure
        Phase objects are left in a consistent state.

        We need to create `Review` objects if the leader and approver review
        data is set in the trs_revision object.

        """
        category = self.document.category
        user_qs = User.objects.filter(categories=category)

        # Is there a defined leader?
        if trs_revision.review_leader:
            self.leader = user_qs.get(name=trs_revision.review_leader)

        # Is there a defined approver
        if trs_revision.review_approver:
            self.approver = user_qs.get(name=trs_revision.review_approver)

        # Was the review started?
        if trs_revision.review_start_date:
            self.start_review(
                at_date=trs_revision.review_start_date,
                due_date=trs_revision.review_due_date)

        # Did the leader already submit a comment?
        if trs_revision.leader_comment_date:
            self.end_leader_step(
                at_date=trs_revision.leader_comment_date,
                save=False)

        # Is there an approver and did he submit a comment?
        if self.approver_id and trs_revision.approver_comment_date:
            self.end_review(
                at_date=trs_revision.approver_comment_date,
                save=False)

        self.save()

    def detail_view_context(self, request):
        """@see `MetadataRevision.detail_view_context`"""
        context = super(ReviewMixin, self).detail_view_context(request)
        user_review = self.get_review(request.user)
        review_closed_on = user_review.closed_on if user_review else None
        context.update({
            'user_review': user_review,
            'review_closed_on': review_closed_on
        })
        return context

    def get_review_fields(self):
        """Return data to display on the review form."""
        fields = [
            (_('Category'), self.document.category),
            (_('Document number'), self.document.document_number),
            (_('Title'), self.document.title),
            (_('Revision'), self.name),
            (_('Status'), self.status),
        ]
        return fields

    def get_actions(self, metadata, user):
        actions = super(ReviewMixin, self).get_actions(metadata, user)
        category = self.document.category

        if self.is_under_review():

            if user.has_perm('documents.can_control_document'):
                actions.insert(-3, MenuItem(
                    'cancel-review',
                    _('Cancel review'),
                    reverse('document_cancel_review', args=[
                        self.document.document_key]),
                    modal='cancel-review-modal'
                ))

            user_review = self.get_review(user)
            review_closed_on = user_review.closed_on if user_review else None
            if review_closed_on:
                actions.insert(-3, MenuItem(
                    'update-comment',
                    _('Modify your comment'),
                    reverse('review_document', args=[
                        self.document.document_key]),
                    method='GET',
                ))

        else:  # revision is not under review
            if self.can_be_reviewed and \
                    user.has_perm('documents.can_control_document'):

                actions.insert(-3, MenuItem(
                    'start-review',
                    _('Start review'),
                    reverse('document_start_review', args=[
                        category.organisation.slug,
                        category.slug,
                        self.document.document_key]),
                ))

                actions.insert(-3, MenuItem(
                    'start-review-remark',
                    _('Start review w/ remark'),
                    reverse('document_start_review', args=[
                        category.organisation.slug,
                        category.slug,
                        self.document.document_key]),
                    modal='start-comment-review'
                ))

        return actions


class DistributionList(models.Model):
    name = models.CharField(
        _('Name'),
        max_length=250)
    categories = models.ManyToManyField(
        'categories.Category',
        verbose_name=_('Category'))
    reviewers = models.ManyToManyField(
        User,
        verbose_name=_('Reviewers'),
        related_name='related_lists_as_reviewer',
        limit_choices_to={'is_external': False},
        blank=True)
    leader = models.ForeignKey(
        User,
        verbose_name=_('Leader'),
        related_name='related_lists_as_leader',
        limit_choices_to={'is_external': False})
    approver = models.ForeignKey(
        User,
        verbose_name=_('Approver'),
        related_name='related_lists_as_approver',
        limit_choices_to={'is_external': False},
        null=True, blank=True)

    class Meta:
        app_label = 'reviews'
        verbose_name = _('Distribution list')
        verbose_name_plural = _('Distribution lists')

    def __unicode__(self):
        return self.name
