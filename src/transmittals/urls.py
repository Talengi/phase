# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from trsimports.views import DiffView, RevisionDiffView

urlpatterns = patterns(
    '',
    url(r'^transmittal/$',
        DiffView.as_view(),
        name="transmittal_diff_view"),

    url(r'^revision/$',
        RevisionDiffView.as_view(),
        name="revision_diff_view"),
)
