import datetime

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.functional import cached_property
from model_utils import Choices

from accounts.models import User
from documents.models import Document
from documents.fields import PrivateFileField
from reviews.fileutils import review_comments_file_path


CLASSES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
)


class Review(models.Model):
    STEPS = Choices(
        ('pending', _('Pending')),
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
    due_date = models.DateField(
        _('Review due date'),
        null=True, blank=True
    )
    docclass = models.IntegerField(
        verbose_name=u"Class",
        default=1,
        choices=CLASSES)
    reviewed_on = models.DateTimeField(
        _('Reviewed on'),
        null=True, blank=True
    )
    closed = models.BooleanField(
        _('Closed'),
        default=False,
    )
    comments = PrivateFileField(
        _('Comments'),
        null=True, blank=True,
        upload_to=review_comments_file_path
    )

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        index_together = (('reviewer', 'document', 'revision', 'role'),)

    @property
    def revision_name(self):
        return '%02d' % self.revision


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
    approver = models.ForeignKey(
        User,
        verbose_name=_('Approver'),
        related_name='%(app_label)s_%(class)s_related_approver',
        null=True, blank=True)
    docclass = models.IntegerField(
        verbose_name=u"Class",
        default=1,
        choices=CLASSES)

    class Meta:
        abstract = True

    @cached_property
    def can_be_reviewed(self):
        """Is this revision ready to be reviewed.

        A revision can only be reviewed if at least a leader was defined.

        Also, a revision can only be reviewed once.

        """
        return all((
            self.leader_id,
            not self.review_start_date
        ))

    @transaction.atomic
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
        self.save(update_document=True)

        for user in self.reviewers.all():
            Review.objects.create(
                reviewer=user,
                document=self.document,
                revision=self.revision,
                due_date=self.review_due_date,
                docclass=self.docclass,
            )

        # Leader is mandatory, no need to test it
        Review.objects.create(
            reviewer=self.leader,
            role=Review.ROLES.leader,
            document=self.document,
            revision=self.revision,
            due_date=self.review_due_date,
            docclass=self.docclass,
        )

        # Approver is not mandatory
        if self.approver_id:
            Review.objects.create(
                reviewer=self.approver,
                role=Review.ROLES.approver,
                document=self.document,
                revision=self.revision,
                due_date=self.review_due_date,
                docclass=self.docclass,
            )

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

    @transaction.atomic
    def end_reviewers_step(self, save=True):
        """Ends the first step of the review."""
        self.reviewers_step_closed = datetime.date.today()

        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=Review.ROLES.reviewer) \
            .update(closed=True)

        if save:
            self.save(update_document=True)

    @transaction.atomic
    def end_leader_step(self, save=True):
        """Ends the second step of the review.

        Also ends the first step if it wasn't already done.

        """
        if self.reviewers_step_closed is None:
            self.end_reviewers_step(save=False)

        self.leader_step_closed = datetime.date.today()

        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=Review.ROLES.leader) \
            .update(closed=True)

        if save:
            self.save(update_document=True)

    @transaction.atomic
    def end_review(self, save=True):
        """Ends the review.

        Also ends the steps before.

        """
        if self.leader_step_closed is None:
            self.end_leader_step(save=False)

        self.review_end_date = datetime.date.today()

        Review.objects \
            .filter(document=self.document) \
            .filter(revision=self.revision) \
            .filter(role=Review.ROLES.approver) \
            .update(closed=True)

        if save:
            self.save(update_document=True)

    def is_under_review(self):
        """It's under review only if review has started but not ended."""
        return bool(self.review_start_date) != bool(self.review_end_date)
    is_under_review.short_description = _('Under review')

    def is_overdue(self):
        today = datetime.date.today()
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

    def is_at_review_step(self, step):
        return step == self.current_review_step()

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

    def is_reviewer(self, user):
        return user in self.reviewers.all()
