from django.conf.urls import patterns, url

from reviews.views import (
    ReviewersDocumentList, LeaderDocumentList, ApproverDocumentList,
    ReviewFormView, StartReview, CancelReview, BatchReview, BatchReviewPoll,
    PrioritiesDocumentList, ReviewHome, CommentsArchiveView,
)

urlpatterns = patterns(
    '',

    # Review home page
    url(r'^$',
        ReviewHome.as_view(),
        name='review_home'),

    # Poll the batch review status
    url(r'^poll/(?P<job_id>[\w-]+)/$',
        BatchReviewPoll.as_view(),
        name='batch_review_poll'),


    # Cancel review
    url(r'^(?P<document_key>[\w-]+)/cancel/$',
        CancelReview.as_view(),
        name="document_cancel_review"),

    # Start review
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?P<document_key>[\w-]+)/$',
        StartReview.as_view(),
        name="document_start_review"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        BatchReview.as_view(),
        name="batch_start_review"),

    # Review steps
    url(r'^priorities/$',
        PrioritiesDocumentList.as_view(),
        name="priorities_review_document_list"),
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

    # Comments download
    url(r'^(?P<document_key>[\w-]+)/(?P<revision>\d+)/comments.zip$',
        CommentsArchiveView.as_view(),
        name="download_review_comments"),
)
