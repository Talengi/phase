from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from reviews.views import (
    BatchStartReview, ReviewersDocumentList, LeaderDocumentList,
    ApproverDocumentList, ReviewFormView
)

urlpatterns = patterns(
    '',

    # Unexisting url, redirect to home
    url(r'^$',
        RedirectView.as_view(url='/')),

    # Batch action
    url(r'^batch/$',
        BatchStartReview.as_view(),
        name="batch_start_review"),

    # Review steps
    url(r'^reviewers/$',
        ReviewersDocumentList.as_view(),
        name="reviewers_review_document_list"),
    url(r'^leader/$',
        LeaderDocumentList.as_view(),
        name="leader_review_document_list"),
    url(r'^approver/$',
        ApproverDocumentList.as_view(),
        name="approver_review_document_list"),

    # Review form
    url(r'^(?P<document_key>[\w-]+)/$',
        ReviewFormView.as_view(),
        name="review_document"),
)
