# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.functional import cached_property
from django.utils import timezone
from django.core.cache import cache
from model_utils import Choices

from accounts.models import User
from documents.models import Document
from privatemedia.fields import PrivateFileField
from reviews.fileutils import review_comments_file_path
from metadata.fields import ConfigurableChoiceField


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
        ('void', ''),
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
        null=True, blank=True
    )
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
        self.closed_on = timezone.now()

        if comments:
            self.status = self.STATUSES.commented
        else:
            self.status = self.STATUSES.reviewed

        if save:
            self.save()


class ReviewMixin(models.Model):
    """A Mixin to use to define reviewable document types."""

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
        cache_key = 'all_reviews_{}'.format(self.document_id)
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

        duration = settings.REVIEW_DURATION
        self.review_due_date = due_date or \
            self.received_date + datetime.timedelta(days=duration)

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
            due_date=self.review_due_date,
            docclass=self.docclass,
            status=leader_review_status,
        )

        # Approver is not mandatory
        if self.approver_id:
            Review.objects.create(
                reviewer_id=self.approver_id,
                role=Review.ROLES.approver,
                document=self.document,
                revision=self.revision,
                due_date=self.review_due_date,
                docclass=self.docclass,
            )

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

        if save:
            self.save(update_document=True)

    def is_under_review(self):
        """It's under review only if review has started but not ended."""
        return bool(self.review_start_date) != bool(self.review_end_date)
    is_under_review.short_description = _('Under review')

    def is_overdue(self):
        today = timezone.now().date()
        return bool(self.review_due_date and self.review_due_date < today)
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
    get_current_review_step_display.short_description = _('Current review step')

    def is_at_review_step(self, step):
        return step == self.current_review_step()

    def get_reviews(self):
        """Get all reviews associated with this revision."""
        qs = Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .order_by('id') \
            .select_related('reviewer')

        return qs

    def get_review(self, user, role='reviewer'):
        """Get the review from this specific user.

        We have to specify the role because, a same user could be reviewer *and*
        leader or approver.

        """
        review = Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=role) \
            .select_related('reviewer') \
            .get(reviewer=user)
        return review

    def get_leader_review(self):
        review = Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role='leader') \
            .select_related('reviewer') \
            .get()
        return review

    def get_approver_review(self):
        review = Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role='approver') \
            .select_related('reviewer') \
            .get()
        return review

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
