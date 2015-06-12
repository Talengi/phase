# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from dashboards.views import IssuedDocsDashboardView

urlpatterns = patterns(
    '',
    url(r'^issued/$',
        IssuedDocsDashboardView.as_view(),
        name="dashboard"),
)
