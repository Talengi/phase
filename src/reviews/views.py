from django.views.generic import ListView, UpdateView
from django.shortcuts import get_object_or_404

from accounts.views import LoginRequiredMixin
from documents.utils import get_all_revision_classes
from documents.models import Document
from reviews.models import ReviewMixin
from reviews.forms import reviewform_factory


class BaseReviewDocumentList(LoginRequiredMixin, ListView):
    template_name = 'reviews/document_list.html'
    context_object_name = 'revisions'

    def get_context_data(self, **kwargs):
        context = super(BaseReviewDocumentList, self).get_context_data(**kwargs)
        context.update({
            'reviews_active': True,
        })
        return context

    def step_filter(self, qs):
        """Filter document list to get reviews at the current step."""
        raise NotImplementedError('Implement me in the child class.')

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

        return revisions


class ReviewersDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the first review step."""

    def step_filter(self, qs):
        return qs \
            .filter(reviewers_step_closed=None) \
            .filter(reviewers=self.request.user)


class LeaderDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the two first review steps."""

    def step_filter(self, qs):
        return qs \
            .filter(leader_step_closed=None) \
            .filter(leader=self.request.user)


class ApproverDocumentList(BaseReviewDocumentList):
    """Display the list of documents at the three review steps."""

    def step_filter(self, qs):
        return qs.filter(approver=self.request.user)


class ReviewForm(LoginRequiredMixin, UpdateView):
    context_object_name = 'revision'
    slug_url_kwarg = 'document_key'
    template_name = 'reviews/review_form.html'

    def get_object(self, queryset=None):
        document_key = self.kwargs.get(self.slug_url_kwarg)
        qs = Document.objects \
            .filter(category__users=self.request.user)

        document = get_object_or_404(qs, document_key=document_key)
        return document.latest_revision

    def get_form_class(self):
        Form = reviewform_factory(self.object.__class__)
        return Form