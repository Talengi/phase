import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from accounts.models import User
from documents.models import Document
from documents.fields import (
    LeaderCommentsFileField, ApproverCommentsFileField, PrivateFileField
)
from reviews.fileutils import reviewers_comments_file_path


class Review(models.Model):
    reviewer = models.ForeignKey(
        User,
        verbose_name=_('User'),
    )
    document = models.ForeignKey(
        Document,
        verbose_name=_('Document')
    )
    revision = models.PositiveIntegerField(
        _('Revision')
    )
    reviewed_on = models.DateField(
        _('Reviewed on'),
        null=True, blank=True
    )
    comments = PrivateFileField(
        _('Comments'),
        null=True, blank=True,
        upload_to=reviewers_comments_file_path
    )

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        index_together = (('reviewer', 'document', 'revision'),)


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
        null=True, blank=True)
    leader = models.ForeignKey(
        User,
        verbose_name=_('Leader'),
        related_name='%(app_label)s_%(class)s_related_leader',
        null=True, blank=True)
    leader_comments = LeaderCommentsFileField(
        _('Leader comments'),
        null=True, blank=True)
    approver = models.ForeignKey(
        User,
        verbose_name=_('Approver'),
        related_name='%(app_label)s_%(class)s_related_approver',
        null=True, blank=True)
    approver_comments = ApproverCommentsFileField(
        _('Approver comments'),
        null=True, blank=True)

    class Meta:
        abstract = True

    def can_be_reviewed(self):
        """Is this revision ready to be reviewed.

        A revision can only be reviewed if all roles have been filled
        (leader, approver and at least one reviewer).

        Also, a revision can only be reviewed once.

        """
        return all((
            self.leader,
            self.approver,
            self.reviewers.count(),
            not self.review_start_date
        ))

    def start_review(self):
        """Starts the review process.

        This methods initiates the review process. We don't check whether the
        document can be reviewed or not, or if the process was already
        initiated. It's up to the developer to perform those checks before
        calling this method.

        """
        today = datetime.date.today()
        duration = settings.REVIEW_DURATION
        self.review_start_date = today
        self.review_due_date = today + datetime.timedelta(days=duration)
        self.save()

    def end_reviewers_step(self, save=True):
        """Ends the first step of the review."""
        self.reviewers_step_closed = datetime.date.today()

        if save:
            self.save()

    def end_leader_step(self, save=True):
        """Ends the second step of the review.

        Also ends the first step if it wasn't already done.

        """
        self.leader_step_closed = datetime.date.today()

        if self.reviewers_step_closed is None:
            self.end_reviewers_step(save=False)

        if save:
            self.save()

    def end_review(self, save=True):
        """Ends the review.

        Also ends the steps before.

        """
        self.review_end_date = datetime.date.today()

        if self.leader_step_closed is None:
            self.end_leader_step(save=False)

        if save:
            self.save()

    def is_under_review(self):
        """It's under review only if review has started but not ended."""
        return bool(self.review_start_date) != bool(self.review_end_date)
    is_under_review.short_description = _('Under review')

    def is_overdue(self):
        today = datetime.date.today()
        return bool(self.review_due_date and self.review_due_date < today)
    is_overdue.short_description = _('Overdue')

    def current_review_step(self):
        """Return a string representing the current step.

            - new
            - reviewers
            - leader
            - approver
            - closed
        """
        if self.review_start_date is None:
            return 'new'

        if self.reviewers_step_closed is None:
            return 'reviewers'

        if self.leader_step_closed is None:
            return 'leader'

        if self.review_end_date is None:
            return 'approver'

        return 'closed'
    current_review_step.short_description = _('Current review step')

    def document_key(self):
        return self.document.document_key
    document_key.short_description = _('Document number')

    def title(self):
        return self.document.title
    title.short_description = _('Title')

    def get_reviews(self):
        """Get all reviews associated with this revision."""
        qs = Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .select_related('reviewer')

        return qs
