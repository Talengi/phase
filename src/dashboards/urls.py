# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from dashboards.views import DashboardView

urlpatterns = patterns(
    '',
    url(r'^$',
        DashboardView.as_view(),
        name="dashboard"),
)
