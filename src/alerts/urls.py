# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from alerts.views import AlertHome, AlertNewDocuments
from alerts.feeds import FeedNewDocuments


urlpatterns = patterns(
    '',
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        AlertHome.as_view(),
        name='alert_home'),

    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/new_documents/$',
        AlertNewDocuments.as_view(),
        name='alert_new_documents'),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/new_documents.rss$',
        FeedNewDocuments.as_view(),
        name='feed_new_documents'),
)
