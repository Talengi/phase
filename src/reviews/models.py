import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from accounts.models import User
from documents.fields import (
    LeaderCommentsFileField, ApproverCommentsFileField
)


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

    def end_review(self):
        """Ends the review.

        Again, we don't validate the document state here. Be responsible.

        """
        self.review_end_date = datetime.date.today()
        self.save()

    def is_under_review(self):
        """It's under review only if review has started but not ended."""
        return bool(self.review_start_date) != bool(self.review_end_date)
    is_under_review.short_description = _('Under review')

    def is_overdue(self):
        today = datetime.date.today()
        return bool(self.review_due_date and self.review_due_date < today)
    is_overdue.short_description = _('Overdue')
