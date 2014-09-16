import datetime

from django.db import transaction
from django.views.generic import View, ListView, DetailView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.db.models import Q
from django.core.cache import cache

from accounts.views import LoginRequiredMixin, PermissionRequiredMixin
from documents.utils import get_all_revision_classes
from documents.models import Document
from documents.views import DocumentListMixin, BaseDocumentList
from reviews.models import ReviewMixin, Review
from notifications.models import notify


class ReviewHome(TemplateView):
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


class BatchReview(BaseDocumentList):
    """Starts the review process more multiple documents at once."""

    def get_redirect_url(self, *args, **kwargs):
        """Redirects to document list after that."""
        return reverse('category_document_list', args=[
            self.kwargs.get('organisation'),
            self.kwargs.get('category')])

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('document_ids')
        docs = self.get_document_class().objects \
            .filter(document_id__in=ids) \
            .select_related('document', 'latest_revision')

        ok = []
        nok = []
        for doc in docs:
            if doc.latest_revision.can_be_reviewed:
                doc.latest_revision.start_review()
                ok.append(doc)
            else:
                nok.append(doc)

        if len(ok) > 0:
            ok_message = ugettext('The review started for the following documents:')
            ok_list = '</li><li>'.join('<a href="%s">%s</a>' % (doc.get_absolute_url(), doc) for doc in ok)
            notify(request.user, '{} <ul><li>{}</li></ul>'.format(
                ok_message,
                ok_list
            ))

            cache.clear()

        if len(nok) > 0:
            nok_message = ugettext("We failed to start the review for the following documents:")
            nok_list = '</li><li>'.join('<a href="%s">%s</a>' % (doc.get_absolute_url(), doc) for doc in nok)
            notify(request.user, '{} <ul><li>{}</li></ul>'.format(
                nok_message,
                nok_list
            ))

        return HttpResponseRedirect(self.get_redirect_url())


class BaseReviewDocumentList(LoginRequiredMixin, ListView):
    template_name = 'reviews/document_list.html'
    context_object_name = 'revisions'

    def breadcrumb_section(self):
        return _('Review'), reverse('review_home')

    def get_context_data(self, **kwargs):
        context = super(BaseReviewDocumentList, self).get_context_data(**kwargs)
        context.update({
            'reviews_active': True,
        })
        return context

    def step_filter(self, qs):
        """Filter document list to get reviews at the current step."""
        raise NotImplementedError('Implement me in the child class.')

    def order_revisions(self, revisions):
        """Return an ordered list of revisions.

        Override in subclasses for a custom sort.

        """
        return revisions

    def get_queryset(self):
        """Base queryset to fetch all documents under review.

        Since documents can be of differente types, we need to launch a query
        for every document type that is reviewable.  We assume that the number
        of reviewable document classes will never be too high, so we don't do
        anything to optimize performances for now.

        """
        revisions = []
        klasses = [klass for klass in get_all_revision_classes() if issubclass(klass, ReviewMixin)]

        for klass in klasses:
            qs = klass.objects \
                .exclude(review_start_date=None) \
                .filter(review_end_date=None) \
                .select_related('document')
            qs = self.step_filter(qs)
            revisions += list(qs)

        return self.order_revisions(revisions)


class PrioritiesDocumentList(BaseReviewDocumentList):
    """High priority document list.

    Document have a high priority if:
     * Due date is < 5 days
     * User is leader or approver
     * Document is of class >= 2

    """
    def breadcrumb_subsection(self):
        return _('Priorities')

    def order_revisions(self, revisions):
        revisions.sort(lambda x, y: cmp(x.review_due_date, y.review_due_date))
        return revisions

    def step_filter(self, qs):
        role_q = Q(leader=self.request.user) | Q(approver=self.request.user)
        delta = datetime.date.today() + datetime.timedelta(days=5)

        qs = qs \
            .filter(role_q) \
            .filter(review_due_date__lte=delta) \
            .filter(klass__lte=2)
        return qs


class ReviewersDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the first review step."""

    def breadcrumb_subsection(self):
        return _('Reviewer')

    def get_pending_reviews(self):
        """Get all pending reviews for this user."""
        if not hasattr(self, '_pending_reviews'):
            reviews = Review.objects \
                .filter(reviewer=self.request.user) \
                .filter(reviewed_on=None) \
                .filter(closed=False)

            self._pending_reviews = reviews.values_list('document_id', flat=True)

        return self._pending_reviews

    def step_filter(self, qs):
        pending_reviews = self.get_pending_reviews()

        # A reviewer can only review a revision once
        # Once it's reviewed, the document should disappear from the list
        return qs \
            .filter(reviewers_step_closed=None) \
            .filter(reviewers=self.request.user) \
            .filter(document_id__in=pending_reviews)


class LeaderDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the two first review steps."""

    def breadcrumb_subsection(self):
        return _('Leader')

    def step_filter(self, qs):
        return qs \
            .filter(leader_step_closed=None) \
            .filter(leader=self.request.user)


class ApproverDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the third review steps."""

    def breadcrumb_subsection(self):
        return _('Approver')

    def step_filter(self, qs):
        return qs.filter(approver=self.request.user)


class ReviewFormView(LoginRequiredMixin, DetailView):
    context_object_name = 'revision'
    template_name = 'reviews/review_form.html'

    def breadcrumb_section(self):
        return _('Review')

    def breadcrumb_object(self):
        return self.object.document

    def get_context_data(self, **kwargs):
        context = super(ReviewFormView, self).get_context_data(**kwargs)

        user = self.request.user

        can_comment = any((
            (self.object.is_at_review_step('approver') and user == self.object.approver),
            (self.object.is_at_review_step('leader') and user == self.object.leader),
            (self.object.is_at_review_step('reviewers') and self.object.is_reviewer(user))
        ))
        context.update({
            'revision': self.object,
            'reviews': self.object.get_reviews(),
            'is_leader': user == self.object.leader,
            'is_approver': user == self.object.approver,
            'can_comment': can_comment,
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

        if revision.is_reviewer(self.request.user) and revision.is_at_review_step('reviewers'):
            qs = Review.objects \
                .filter(document=document) \
                .filter(reviewer=self.request.user) \
                .filter(revision=revision.revision)
            self.review = get_object_or_404(qs)

        return revision

    def get_success_url(self):
        if self.request.user == self.object.approver:
            url = 'approver_review_document_list'
        elif self.request.user == self.object.leader:
            url = 'leader_review_document_list'
        else:
            url = 'reviewers_review_document_list'

        return reverse(url)

    def post(self, request, *args, **kwargs):
        """Process the submitted file and form.

        Multiple cases:
          - A reviewer is submitting a review, submitting a file or not
          - The leader is closing the reviewer step
          - The leader is submitting it's review, with or without file
          - The approver is closing the reviewer step
          - The approver is closing the leader step
          - The approver is submitting it's review, with or without file

        """
        self.object = self.get_object()

        step = self.object.current_review_step()
        step_method = '%s_step_post' % step

        if 'review' in request.POST:
            url = self.get_success_url()
        else:
            url = ''

        # A comment file was submitted
        if hasattr(self, step_method) and 'review' in request.POST:
            getattr(self, step_method)(request, *args, **kwargs)

        # Close XXX step buttons

        if 'close_reviewers_step' in request.POST and request.user in (
                self.object.leader, self.object.approver):
            self.object.end_reviewers_step()

        if 'close_leader_step' in request.POST and request.user == self.object.approver:
            self.object.end_leader_step()

        return HttpResponseRedirect(url)

    @transaction.atomic
    def reviewers_step_post(self, request, *args, **kwargs):
        comments_file = request.FILES.get('comments', None)

        if hasattr(self, 'review'):
            self.review.reviewed_on = datetime.date.today()
            self.review.comments = comments_file
            self.review.closed = True
            self.review.save()

            # If every reviewer has posted comments, close the reviewers step
            qs = Review.objects \
                .filter(document=self.object.document) \
                .filter(revision=self.object.revision) \
                .exclude(reviewed_on=None)
            if qs.count() == self.object.reviewers.count():
                self.object.end_reviewers_step()

    def leader_step_post(self, request, *args, **kwargs):
        comments_file = request.FILES.get('comments', None)

        if self.object.leader == request.user:
            self.object.leader_comments = comments_file
            self.object.end_leader_step(save=False)
            self.object.save()

    def approver_step_post(self, request, *args, **kwargs):
        comments_file = request.FILES.get('comments', None)

        if self.object.approver == request.user:
            self.object.approver_comments = comments_file
            self.object.end_review(save=False)
            self.object.save()
