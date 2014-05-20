from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from reviews.views import (
    ReviewersDocumentList, LeaderDocumentList, ApproverDocumentList,
    ReviewFormView, StartReview, BatchReview
)

urlpatterns = patterns(
    '',

    # Unexisting url, redirect to home
    url(r'^$',
        RedirectView.as_view(url='/')),

    # Start review
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?P<document_key>[\w-]+)/$',
        StartReview.as_view(),
        name="document_start_review"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        BatchReview.as_view(),
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
