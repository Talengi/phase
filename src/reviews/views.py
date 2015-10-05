# -*- coding: utf-8 -*-

import datetime
import json

from django.db import transaction
from django.views.generic import View, ListView, DetailView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.models import modelform_factory
from django.utils import timezone

from celery.result import AsyncResult
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from zipview.views import BaseZipView

from documents.models import Document
from documents.views import DocumentListMixin, BaseDocumentList
from discussion.models import Note
from notifications.models import notify
from reviews.models import Review
from reviews.tasks import do_batch_import


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


class BatchReview(BaseDocumentList):
    """Starts the review process for multiple documents at once.

    This operation can be quite time consuming when many documents are reviewed
    at once, and this is expected to be normal by the users. We display a nice
    progress bar while the user waits.

    Since the user is already waiting, we also perform elasticsearch indexing
    synchronously, so at the end of the operation, the document list displayed
    is in sync.

    """
    def get_redirect_url(self, *args, **kwargs):
        """Redirects to document list after that."""
        return reverse('category_document_list', args=[
            self.kwargs.get('organisation'),
            self.kwargs.get('category')])

    def post(self, request, *args, **kwargs):
        document_ids = request.POST.getlist('document_ids')
        document_class = self.get_document_class()
        contenttype = ContentType.objects.get_for_model(document_class)

        job = do_batch_import.delay(request.user.id, contenttype.id, document_ids)

        poll_url = reverse('batch_review_poll', args=[job.id])
        data = {'poll_url': poll_url}
        return HttpResponse(json.dumps(data), content_type='application/json')


class BatchReviewPoll(View):
    """Display information about the ongoing batch review task.

    This view is intended to be polled with ajax.

    Since the displayed information is not critical, and the job id is
    auto-generated, we don't perform any acl verification.

    """

    def get(self, request, job_id):
        """Return json data to describe the task."""
        job = AsyncResult(job_id)

        done = job.ready()
        result = job.result
        if isinstance(result, dict):
            current = result['current']
            total = result['total']
            progress = float(current) / total * 100
        else:
            progress = 100.0 if done else 0.0

        data = {
            'done': done,
            'progress': progress
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


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

    def get_context_data(self, **kwargs):
        context = super(ReviewFormView, self).get_context_data(**kwargs)

        user = self.request.user
        is_reviewer = self.object.is_reviewer(user)
        is_leader = user == self.object.leader
        is_approver = user == self.object.approver

        reviews = self.object.get_reviews()
        can_comment = any((
            (self.object.is_at_review_step('approver') and is_approver),
            (self.object.is_at_review_step('leader') and is_leader),
            (self.object.is_at_review_step('reviewer') and is_reviewer)
        ))
        close_reviewers_button = self.object.is_at_review_step('reviewer') and (is_leader or is_approver)
        close_leader_button = self.object.is_at_review_step('leader') and is_approver
        back_to_leader_button = self.object.is_at_review_step('approver') and is_approver

        # Only members of the distrib list can see the review form
        # so the user is automaticaly allowed to post a remark
        can_discuss = True

        # Which form fields should we display?
        fields = ('comments',)
        if is_leader or is_approver:
            fields += ('return_code',)
        form = modelform_factory(Review, fields=fields, labels={
            'comments': _('Upload your comments'),
            'return_code': _('Select a return code'),
        })

        context.update({
            'document': self.object.document,
            'document_key': self.object.document.document_key,
            'revision': self.object,
            'reviews': reviews,
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

    def check_permission(self, revision, user):
        """Test the user permission to access the current step.

          - A reviewer can only access the review at the fisrt step
          - The leader can access the review at the two first steps
          - The approver can access the review at any step
        """
        if not revision.is_under_review():
            raise Http404()

        # Approver can acces all steps
        elif user == revision.approver:
            pass

        # Leader can only access steps <= approver step
        elif user == revision.leader:
            if revision.leader_step_closed:
                raise Http404()

        # Reviewers can only access the first step
        elif revision.is_reviewer(user):
            if revision.reviewers_step_closed:
                raise Http404()

        # User is not even part of the review
        else:
            raise Http404()

    def get_object(self, queryset=None):
        document_key = self.kwargs.get('document_key')
        qs = Document.objects \
            .filter(category__users=self.request.user)
        document = get_object_or_404(qs, document_key=document_key)
        revision = document.latest_revision

        self.check_permission(revision, self.request.user)

        return revision

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

        # A review was posted, with or without file
        if 'review' in request.POST:
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
        step = self.object.current_review_step()
        comments_file = request.FILES.get('comments', None)
        return_code = request.POST.get('return_code', None)

        # Get the current review being submitted…
        qs = Review.objects \
            .filter(document=document) \
            .filter(revision=revision.revision) \
            .filter(reviewer=request.user) \
            .filter(role=step)
        review = get_object_or_404(qs)

        # … and update it
        review.post_review(comments_file, return_code=return_code)
        if return_code:
            revision.return_code = return_code

        # If every reviewer has posted comments, close the reviewers step
        if self.object.is_at_review_step('reviewer'):
            qs = Review.objects \
                .filter(document=document) \
                .filter(revision=revision.revision) \
                .filter(role='reviewer') \
                .exclude(closed_on=None)
            if qs.count() == self.object.reviewers.count():
                self.object.end_reviewers_step(save=False)

        # If leader, end leader step
        elif self.object.is_at_review_step('leader'):
            self.object.end_leader_step(save=False)

        # If approver, end approver step
        elif self.object.is_at_review_step('approver'):
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
