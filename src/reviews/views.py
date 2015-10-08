# -*- coding: utf-8 -*-

import datetime
import json

from django.db import transaction
from django.views.generic import View, ListView, DetailView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from django.http import (HttpResponse, HttpResponseRedirect, Http404,
                         HttpResponseForbidden)
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.models import modelform_factory
from django.utils import timezone

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from zipview.views import BaseZipView

from documents.models import Document
from documents.views import DocumentListMixin, BaseDocumentList
from discussion.models import Note
from notifications.models import notify
from reviews.models import Review
from reviews.tasks import (do_batch_import, batch_close_reviews,
                           batch_cancel_reviews)


class ReviewHome(LoginRequiredMixin, TemplateView):
    template_name = 'reviews/home.html'

    def breadcrumb_section(self):
        return _('Review'), reverse('review_home')


class StartReview(PermissionRequiredMixin,
                  DocumentListMixin,
                  SingleObjectMixin,
                  View):
    """Start the review process."""
    permission_required = 'documents.can_control_document'
    context_object_name = 'metadata'

    def get_redirect_url(self, *args, **kwargs):
        document = self.metadata.document
        return reverse('document_detail', args=[
            document.category.organisation.slug,
            document.category.slug,
            document.document_key])

    def post(self, request, *args, **kwargs):
        self.metadata = self.get_object()
        revision = self.metadata.latest_revision
        document = self.metadata.document

        if revision.can_be_reviewed:
            revision.start_review()

            # If a non empty message body was submitted...
            body = self.request.POST.get('body', None)
            if body:
                Note.objects.create(
                    author=self.request.user,
                    document=document,
                    revision=revision.revision,
                    body=body)

            message_text = '''You started the review on revision %(rev)s of
                           the document <a href="%(url)s">%(key)s (%(title)s)</a>'''
            message_data = {
                'rev': revision.name,
                'url': document.get_absolute_url(),
                'key': document.document_key,
                'title': document.title
            }
            notify(request.user, _(message_text) % message_data)
        else:
            message_text = '''The review on revision %(rev)s of the document
                           <a href="%(url)s">%(key)s (%(title)s)</a>
                           cannot be started'''
            message_data = {
                'rev': revision.name,
                'url': document.get_absolute_url(),
                'key': document.document_key,
                'title': document.title
            }
            notify(request.user, _(message_text) % message_data)

        return HttpResponseRedirect(self.get_redirect_url())


class CancelReview(PermissionRequiredMixin,
                   SingleObjectMixin,
                   View):
    """Cancel the review process."""
    permission_required = 'documents.can_control_document'
    context_object_name = 'metadata'

    def get_object(self, queryset=None):
        document_key = self.kwargs.get('document_key')
        qs = Document.objects \
            .filter(category__users=self.request.user)
        document = get_object_or_404(qs, document_key=document_key)
        return document.metadata

    def get_redirect_url(self, *args, **kwargs):
        """Get the url to redirect to.

        Reviews can be canceled from two places:
          - the review form
          - the document form

        In the first case, the user should be redirected to review list.
        In the second, the user should be redirected to the same form.

        """
        referer = self.request.META.get('HTTP_REFERER', '')
        if 'reviews' in referer:
            url = reverse('review_home')
        else:
            document = self.metadata.document
            url = reverse('document_detail', args=[
                document.category.organisation.slug,
                document.category.slug,
                document.document_key])

        return url

    def post(self, request, *args, **kwargs):
        self.metadata = self.get_object()
        revision = self.metadata.latest_revision
        document = self.metadata.document

        if revision.is_under_review():
            revision.cancel_review()
            message_text = '''You cancelled the review on revision %(rev)s of
                           the document <a href="%(url)s">%(key)s (%(title)s)</a>'''
            message_data = {
                'rev': revision.name,
                'url': document.get_absolute_url(),
                'key': document.document_key,
                'title': document.title
            }
            notify(request.user, _(message_text) % message_data)

        return HttpResponseRedirect(self.get_redirect_url())


class BaseBatchView(PermissionRequiredMixin, BaseDocumentList):
    """Performs a task on several reviews at once.

    This operation can be quite time consuming when many documents are reviewed
    at once, and this is expected to be normal by the users. We display a nice
    progress bar while the user waits.

    Since the user is already waiting, we also perform elasticsearch indexing
    synchronously, so at the end of the operation, the document list displayed
    is in sync.

    """
    permission_required = 'documents.can_control_document'

    def get_redirect_url(self, *args, **kwargs):
        """Redirects to document list after that."""
        return reverse('category_document_list', args=[
            self.kwargs.get('organisation'),
            self.kwargs.get('category')])

    def post(self, request, *args, **kwargs):
        document_ids = request.POST.getlist('document_ids')
        document_class = self.get_document_class()
        contenttype = ContentType.objects.get_for_model(document_class)

        job = self.start_job(contenttype, document_ids)

        poll_url = reverse('task_poll', args=[job.id])
        data = {'poll_url': poll_url}
        return HttpResponse(json.dumps(data), content_type='application/json')

    def start_job(self, content_type, document_ids):
        raise NotImplementedError()


class BatchStartReviews(BaseBatchView):
    """Starts the review process for multiple documents at once."""

    def start_job(self, contenttype, document_ids):
        job = do_batch_import.delay(
            self.request.user.id,
            self.category.id,
            contenttype.id,
            document_ids)
        return job


class BatchCancelReviews(BaseBatchView):
    """Cancel several reviews at once."""

    def start_job(self, contenttype, document_ids):
        job = batch_cancel_reviews.delay(
            self.request.user.id,
            self.category.id,
            contenttype.id,
            document_ids)
        return job


class BaseReviewDocumentList(LoginRequiredMixin, ListView):
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'

    def breadcrumb_section(self):
        return _('Reviews'), reverse('review_home')

    def get_context_data(self, **kwargs):
        context = super(BaseReviewDocumentList, self).get_context_data(**kwargs)
        context.update({
            'reviews_active': True,
            'review_step': self.review_step,
            'current_url': self.request.path,
        })
        return context

    def step_filter(self, qs):
        """Filter document list to get reviews at the current step."""
        raise NotImplementedError('Implement me in the child class.')

    def order_reviews(self, reviews):
        """Return an ordered list of reviews.

        Override in subclasses for a custom sort.

        """
        return reviews

    def get_queryset(self):
        """Base queryset to fetch all waiting reviews."""
        reviews = Review.objects \
            .filter(reviewer=self.request.user) \
            .filter(closed_on=None) \
            .order_by('due_date') \
            .select_related()
        reviews = self.step_filter(reviews)
        return reviews


class PrioritiesDocumentList(BaseReviewDocumentList):
    """High priority document list.

    Document have a high priority if:
     * Due date is < 5 days
     * User is leader or approver
     * Document is of class >= 2

    """
    review_step = 'priorities'

    def breadcrumb_subsection(self):
        return _('Priorities')

    def step_filter(self, qs):
        role_q = Q(role='leader') | Q(role='approver')
        delta = timezone.now() + datetime.timedelta(days=5)

        qs = qs \
            .filter(role_q) \
            .filter(due_date__lte=delta) \
            .filter(docclass__lte=2)
        return qs


class ReviewersDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the first review step."""
    review_step = 'reviewer'

    def breadcrumb_subsection(self):
        return _('Reviewer')

    def step_filter(self, qs):
        return qs.filter(role=Review.ROLES.reviewer)

    def post(self, request, *args, **kwargs):
        review_ids = request.POST.getlist('review_ids')

        job = batch_close_reviews.delay(request.user.id, review_ids)

        poll_url = reverse('task_poll', args=[job.id])
        data = {'poll_url': poll_url}
        return HttpResponse(json.dumps(data), content_type='application/json')


class LeaderDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the two first review steps."""
    review_step = 'leader'

    def breadcrumb_subsection(self):
        return _('Leader')

    def step_filter(self, qs):
        return qs.filter(role=Review.ROLES.leader)


class ApproverDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the third review steps."""
    review_step = 'approver'

    def breadcrumb_subsection(self):
        return _('Approver')

    def step_filter(self, qs):
        return qs.filter(role=Review.ROLES.approver)


# TODO Refactor to use UpdateView
class ReviewFormView(LoginRequiredMixin, DetailView):
    context_object_name = 'revision'
    template_name = 'reviews/review_form.html'

    def breadcrumb_section(self):
        return (_('Reviews'), reverse('review_home'))

    def breadcrumb_subsection(self):
        if self.request.user == self.object.approver:
            url = (_('Approver'), reverse('approver_review_document_list'))
        elif self.request.user == self.object.leader:
            url = (_('Leader'), reverse('leader_review_document_list'))
        else:
            url = (_('Reviewer'), reverse('reviewers_review_document_list'))
        return url

    def breadcrumb_object(self):
        return self.object.document

    def get_object(self, queryset=None):
        document_key = self.kwargs.get('document_key')
        qs = Document.objects \
            .filter(category__users=self.request.user)
        document = get_object_or_404(qs, document_key=document_key)
        revision = document.latest_revision

        return revision

    def check_permission(self, user, revision, review):
        """Test the user permission to access the current step.

        Every member of the distribution list can access the review at any
        moment.

        Note that commenting permission is tested elsewhere.

        """
        # Document is not even under review
        if not revision.is_under_review():
            raise Http404()

        # User is not a member of the distribution list
        elif review is None:
            raise Http404()

        else:
            pass

    def get_context_data(self, **kwargs):
        context = super(ReviewFormView, self).get_context_data(**kwargs)

        user = self.request.user
        user_review = self.object.get_review(user)
        all_reviews = self.object.get_reviews()

        self.check_permission(user, self.object, user_review)

        is_reviewer = user_review.role == 'reviewer'
        is_leader = user_review.role == 'leader'
        is_approver = user_review.role == 'approver'

        # Users can update their comment even if they already
        # posted something.
        can_comment = user_review.status not in ('pending',)

        close_reviewers_button = self.object.is_at_review_step('reviewer') and (is_leader or is_approver)
        close_leader_button = self.object.is_at_review_step('leader') and is_approver
        back_to_leader_button = self.object.is_at_review_step('approver') and is_approver

        # every member of the distrib list can see the review form
        # so the user is automaticaly allowed to post a remark
        can_discuss = True

        # Which form fields should we display?
        fields = ('comments',)
        if is_leader or is_approver:
            fields += ('return_code',)
        Form = modelform_factory(Review, fields=fields, labels={
            'comments': _('Upload your comments'),
            'return_code': _('Select a return code'),
        })
        form = Form(instance=user_review)

        context.update({
            'document': self.object.document,
            'document_key': self.object.document.document_key,
            'revision': self.object,
            'reviews': all_reviews,
            'leader': self.object.leader,
            'is_reviewer': is_reviewer,
            'is_leader': is_leader,
            'is_approver': is_approver,
            'can_comment': can_comment,
            'close_reviewers_button': close_reviewers_button,
            'close_leader_button': close_leader_button,
            'back_to_leader_button': back_to_leader_button,
            'can_discuss': can_discuss,
            'form': form,
        })
        return context

    def get_success_url(self):
        """Generate correct url after form submission.

        There are a few different cases:

            * If a review was submitted, go back to the review list.
            * If an approver sends the document back, go back to the review list.
            * In any other cases, stay on the page.

        """
        if (any((
                'review' in self.request.POST,
                'back_to_leader_step' in self.request.POST,))):
            # Send back to the correct list
            if self.request.user == self.object.approver:
                url = 'approver_review_document_list'
            elif self.request.user == self.object.leader:
                url = 'leader_review_document_list'
            else:
                url = 'reviewers_review_document_list'

            url = reverse(url)

        else:
            url = ''

        return url

    def post(self, request, *args, **kwargs):
        """Process the submitted file and form.

        Multiple cases:
          - A reviewer/leader/approver is submitting a review, withe a comment file or not
          - The leader is closing the reviewer step
          - The approver is closing the reviewer step
          - The approver is closing the leader step
          - The approver is sending the review back to leader step

        """
        self.object = self.get_object()
        user = self.request.user
        user_review = self.object.get_review(user)
        self.check_permission(user, self.object, user_review)

        # A review was posted, with or without file
        if 'review' in request.POST:

            # Can the user really comment?
            can_comment = user_review.status not in ('pending',)
            if not can_comment:
                return HttpResponseForbidden()

            self.post_review(request, *args, **kwargs)

            comments_file = request.FILES.get('comments', None)
            if comments_file:
                message_text = '''You reviewed the document
                               <a href="%(url)s">%(key)s (%(title)s)</a>
                               in revision %(rev)s with comments.'''
            else:
                message_text = '''You reviewed the document
                               <a href="%(url)s">%(key)s (%(title)s)</a>
                               in revision %(rev)s without comments.'''

            document = self.object.document
            message_data = {
                'rev': self.object.name,
                'url': document.get_absolute_url(),
                'key': document.document_key,
                'title': document.title
            }
            notify(request.user, _(message_text) % message_data)

        if 'close_reviewers_step' in request.POST and request.user in (
                self.object.leader, self.object.approver):
            self.object.end_reviewers_step()

        if 'close_leader_step' in request.POST and request.user == self.object.approver:
            self.object.end_leader_step()

        if 'back_to_leader_step' in request.POST and request.user == self.object.approver:
            self.object.send_back_to_leader_step()
            body = request.POST.get('body', None)
            if body:
                Note.objects.create(
                    author=request.user,
                    document=self.object.document,
                    revision=self.object.revision,
                    body=body)

        url = self.get_success_url()
        return HttpResponseRedirect(url)

    @transaction.atomic
    def post_review(self, request, *args, **kwargs):
        """Update the Review object with posted data.

        Also, updates the document if any review step is finished.

        """
        document = self.object.document
        revision = self.object
        comments_file = request.FILES.get('comments', None)
        return_code = request.POST.get('return_code', None)

        # Get the current review being edited
        review = revision.get_review(request.user)

        # … and update it
        review.post_review(comments_file, return_code=return_code)
        if return_code:
            revision.return_code = return_code

        # If every reviewer has posted comments, close the reviewers step
        if review.role == 'reviewer':
            qs = Review.objects \
                .filter(document=document) \
                .filter(revision=revision.revision) \
                .filter(role='reviewer') \
                .exclude(closed_on=None)
            if qs.count() == self.object.reviewers.count():
                self.object.end_reviewers_step(save=False)

        # If leader, end leader step
        elif review.role == 'leader':
            self.object.end_leader_step(save=False)

        # If approver, end approver step
        elif review.role == 'approver':
            self.object.end_review(save=False)

        self.object.save(update_document=True)


class CommentsArchiveView(LoginRequiredMixin, BaseZipView):
    """Download at once all comments for a review."""

    zipfile_name = 'comments.zip'

    def get_files(self):
        revision = self.kwargs.get('revision')
        document_key = self.kwargs.get('document_key')
        reviews = Review.objects \
            .filter(revision=revision) \
            .filter(document__document_key=document_key) \
            .exclude(comments__isnull=True)

        return [review.comments.file for review in reviews if review.comments.name]
