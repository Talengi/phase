# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from dashboards.views import IssuedDocsDashboardView, ReturnedDocsDashboardView

urlpatterns = patterns(
    '',
    url(r'^issued/$',
        IssuedDocsDashboardView.as_view(),
        name="issued_dashboard"),
    url(r'^returned/$',
        ReturnedDocsDashboardView.as_view(),
        name="returned_dashboard"),
)
