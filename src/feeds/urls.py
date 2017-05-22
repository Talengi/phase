# -*- coding: utf-8 -*-


from django.conf.urls import url

from feeds.views import (
    AlertHome, AlertNewDocuments, AlertClosedReviews, AlertStartedReviews,
    AlertOverdueDocuments)
from feeds.feeds import (
    FeedNewDocuments, FeedClosedReviews, FeedStartedReviews,
    FeedOverdueDocuments)


urlpatterns = [
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        AlertHome.as_view(),
        name='category_feeds'),

    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/new_documents/$',
        AlertNewDocuments.as_view(),
        name='alert_new_documents'),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/new_documents.rss$',
        FeedNewDocuments.as_view(),
        name='feed_new_documents'),

    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/closed_reviews/$',
        AlertClosedReviews.as_view(),
        name='alert_closed_reviews'),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/closed_reviews.rss$',
        FeedClosedReviews.as_view(),
        name='feed_closed_reviews'),

    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/under_review/$',
        AlertStartedReviews.as_view(),
        name='alert_started_reviews'),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/under_review.rss$',
        FeedStartedReviews.as_view(),
        name='feed_started_reviews'),

    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/overdue_documents/$',
        AlertOverdueDocuments.as_view(),
        name='alert_overdue_documents'),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/overdue_documents.rss$',
        FeedOverdueDocuments.as_view(),
        name='feed_overdue_documents'),
]
