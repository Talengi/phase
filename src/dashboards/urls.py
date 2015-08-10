# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from django.conf.urls import patterns, url

from dashboards.views import DashboardView

urlpatterns = patterns(
    '',
    url(r'^(?P<organisation>[\w-]+)/dashboards/(?P<dashboard>[\w-]+)/$',
        DashboardView.as_view(),
        name='dashboard_detail'),
)
