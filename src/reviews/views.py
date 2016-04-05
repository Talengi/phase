# -*- coding: utf-8 -*-

import datetime
import json

from django.db import transaction
from django.views.generic import (
    View, ListView, UpdateView, TemplateView, DetailView)
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from django.http import (HttpResponse, HttpResponseRedirect, Http404,
                         HttpResponseForbidden)
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.forms.models import modelform_factory
from django.utils import timezone

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from zipview.views import BaseZipView

from audit_trail.models import Activity
from audit_trail.signals import activity_log
from documents.models import Document
from documents.views import DocumentListMixin, BaseDocumentBatchActionView
from discussion.models import Note
from notifications.models import notify
from reviews.models import Review
from reviews.tasks import (do_batch_import, batch_close_reviews,
                           batch_cancel_reviews)
from reviews.forms import BasePostReviewForm, ReviewSearchForm
from privatemedia.views import serve_model_file_field


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
            activity_log.send(verb=Activity.VERB_STARTED_REVIEW,
                              target=revision,
                              sender=None,
                              actor=self.request.user)
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
            activity_log.send(verb=Activity.VERB_CANCELLED_REVIEW,
                              target=revision,
                              sender=None,
                              actor=self.request.user)
        return HttpResponseRedirect(self.get_redirect_url())


class BatchStartReviews(PermissionRequiredMixin, BaseDocumentBatchActionView):
    """Starts the review process for multiple documents at once."""
    permission_required = 'documents.can_control_document'

    def start_job(self, contenttype, document_ids):
        remark = self.request.POST.get('remark', None)
        job = do_batch_import.delay(
            self.request.user.id,
            self.category.id,
            contenttype.id,
            document_ids,
            remark=remark)
        return job


class BatchCancelReviews(PermissionRequiredMixin, BaseDocumentBatchActionView):
    """Cancel several reviews at once."""
    permission_required = 'documents.can_control_document'

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

    def get_search_form(self, reviews):
        form = ReviewSearchForm(
            self.request.GET or None,
            user=self.request.user,
            reviews=reviews)
        return form

    def get_context_data(self, **kwargs):
        context = super(BaseReviewDocumentList, self).get_context_data(**kwargs)
        context.update({
            'reviews_active': True,
            'review_step': self.review_step,
            'current_url': self.request.path,
            'search_form': self.search_form,
        })
        return context

    def step_filter(self, qs):
        """Filter document list to get reviews at the current step."""
        return qs

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

        self.search_form = self.get_search_form(reviews)
        reviews = self.search_form.filter_reviews()

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
        qs = super(PrioritiesDocumentList, self).step_filter(qs)
        role_q = Q(role='leader') | Q(role='approver')
        delta = timezone.now() + datetime.timedelta(days=5)

        qs = qs.filter(role_q) \
            .filter(due_date__lte=delta) \
            .filter(docclass__lte=2)
        return qs


class ReviewersDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the first review step."""
    review_step = 'reviewer'

    def breadcrumb_subsection(self):
        return _('Reviewer')

    def step_filter(self, qs):
        qs = super(ReviewersDocumentList, self).step_filter(qs)
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
        qs = super(LeaderDocumentList, self).step_filter(qs)
        return qs.filter(role=Review.ROLES.leader)


class ApproverDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the third review steps."""
    review_step = 'approver'

    def breadcrumb_subsection(self):
        return _('Approver')

    def step_filter(self, qs):
        qs = super(ApproverDocumentList, self).step_filter(qs)
        return qs.filter(role=Review.ROLES.approver)


class ReviewFormView(LoginRequiredMixin, UpdateView):
    context_object_name = 'review'
    template_name = 'reviews/review_form.html'

    def breadcrumb_section(self):
        return (_('Reviews'), reverse('review_home'))

    def breadcrumb_subsection(self):
        if self.request.user == self.revision.approver:
            url = (_('Approver'), reverse('approver_review_document_list'))
        elif self.request.user == self.revision.leader:
            url = (_('Leader'), reverse('leader_review_document_list'))
        else:
            url = (_('Reviewer'), reverse('reviewers_review_document_list'))
        return url

    def breadcrumb_object(self):
        return self.document

    def get_object(self, queryset=None):
        document_key = self.kwargs.get('document_key')
        qs = Document.objects \
            .filter(category__users=self.request.user) \
            .select_related()
        document = get_object_or_404(qs, document_key=document_key)
        revision = document.latest_revision
        review = revision.get_review(self.request.user)

        if review is None:
            raise Http404()

        # For better performance
        self.document = document
        self.revision = revision

        return review

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
        if review is None:
            raise Http404()

    def get_form_class(self):
        # Which form fields should we display?
        fields = ('comments',)

        if self.object.role in ('leader', 'approver'):
            fields += ('return_code',)
        Form = modelform_factory(
            Review,
            fields=fields,
            form=BasePostReviewForm,
            labels={
                'comments': _('Upload your comments'),
                'return_code': _('Select a return code')})
        return Form

    def get_context_data(self, **kwargs):
        context = super(ReviewFormView, self).get_context_data(**kwargs)

        user = self.request.user
        user_review = self.object
        all_reviews = self.revision.get_reviews()

        self.check_permission(user, self.revision, user_review)

        is_reviewer = user_review.role == 'reviewer'
        is_leader = user_review.role == 'leader'
        is_approver = user_review.role == 'approver'

        # Users can update their comment even if they already
        # posted something.
        can_comment = user_review.status not in ('pending',)

        close_reviewers_button = self.revision.is_at_review_step('reviewer') and (is_leader or is_approver)
        close_leader_button = self.revision.is_at_review_step('leader') and is_approver
        back_to_leader_button = self.revision.is_at_review_step('approver') and is_approver

        # every member of the distrib list can see the review form
        # so the user is automaticaly allowed to post a remark
        can_discuss = True

        context.update({
            'document': self.document,
            'document_key': self.document.document_key,
            'revision': self.revision,
            'reviews': all_reviews,
            'leader': self.revision.leader,
            'is_reviewer': is_reviewer,
            'is_leader': is_leader,
            'is_approver': is_approver,
            'can_comment': can_comment,
            'close_reviewers_button': close_reviewers_button,
            'close_leader_button': close_leader_button,
            'back_to_leader_button': back_to_leader_button,
            'can_discuss': can_discuss,
            'fields': self.revision.get_review_fields(),
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
            if self.request.user == self.revision.approver:
                url = 'approver_review_document_list'
            elif self.request.user == self.revision.leader:
                url = 'leader_review_document_list'
            else:
                url = 'reviewers_review_document_list'

            url = reverse(url)

        else:
            url = ''

        return url

    def form_valid(self, form):
        """Process the submitted file and form.

        Multiple cases:
          - A reviewer/leader/approver is submitting a review, withe a comment file or not
          - The leader is closing the reviewer step
          - The approver is closing the reviewer step
          - The approver is closing the leader step
          - The approver is sending the review back to leader step

        """
        user = self.request.user
        self.check_permission(user, self.revision, self.object)

        # A review was posted, with or without file
        if 'review' in self.request.POST:

            # Can the user really comment?
            can_comment = self.object.status not in ('pending',)
            if not can_comment:
                return HttpResponseForbidden()

            self.post_review(form)

            comments_file = form.cleaned_data.get('comments', None)
            if comments_file:
                message_text = '''You reviewed the document
                               <a href="%(url)s">%(key)s (%(title)s)</a>
                               in revision %(rev)s with comments.'''
            else:
                message_text = '''You reviewed the document
                               <a href="%(url)s">%(key)s (%(title)s)</a>
                               in revision %(rev)s without comments.'''

            message_data = {
                'rev': self.revision.name,
                'url': self.document.get_absolute_url(),
                'key': self.document.document_key,
                'title': self.document.title
            }
            notify(user, _(message_text) % message_data)

        if 'close_reviewers_step' in self.request.POST and user in (
                self.revision.leader, self.revision.approver):
            self.revision.end_reviewers_step()

        if 'close_leader_step' in self.request.POST and user == self.revision.approver:
            self.revision.end_leader_step()

        if 'back_to_leader_step' in self.request.POST and user == self.revision.approver:
            self.revision.send_back_to_leader_step()
            body = self.request.POST.get('body', None)
            if body:
                Note.objects.create(
                    author=user,
                    document=self.document,
                    revision=self.revision,
                    body=body)

        url = self.get_success_url()
        return HttpResponseRedirect(url)

    @transaction.atomic
    def post_review(self, form):
        """Update the Review object with posted data.

        Also, updates the document if any review step is finished.

        """
        comments_file = form.cleaned_data.get('comments', None)
        return_code = form.cleaned_data.get('return_code', None)

        # Update the review
        self.object.post_review(comments_file, return_code=return_code)
        if return_code:
            self.revision.return_code = return_code

        # If every reviewer has posted comments, close the reviewers step
        if self.object.role == 'reviewer':
            qs = Review.objects \
                .filter(document=self.document) \
                .filter(revision=self.revision.revision) \
                .filter(role='reviewer') \
                .exclude(closed_on=None)
            if qs.count() == self.revision.reviewers.count():
                self.revision.end_reviewers_step(save=False)

        # If leader, end leader step
        elif self.object.role == 'leader':
            self.revision.end_leader_step(save=False)

        # If approver, end approver step
        elif self.object.role == 'approver':
            self.revision.end_review(save=False)

        self.revision.save(update_document=True)


class CommentsDownload(LoginRequiredMixin, DetailView):
    """Download a single comments file."""

    http_method_names = ['get']

    def get_object(self, queryset=None):
        key = self.kwargs.get('document_key')
        revision = self.kwargs.get('revision')
        review_id = self.kwargs.get('review_id')

        qs = Review.objects \
            .filter(document__document_key=key) \
            .filter(revision=revision) \
            .filter(id=review_id) \
            .filter(document__category=self.request.user.categories.all())
        review = get_object_or_404(qs)
        return review

    def get(self, request, *args, **kwargs):
        review = self.get_object()

        if not review.comments:
            raise Http404('This review has no comments')

        return serve_model_file_field(review, 'comments')


class CommentsArchiveDownload(LoginRequiredMixin, BaseZipView):
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
