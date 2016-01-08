# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from transmittals.views import (
    TransmittalListView, TransmittalDiffView, TransmittalRevisionDiffView,
    TransmittalDownloadView, PrepareTransmittalView, CreateTransmittalView)

urlpatterns = patterns(
    '',
    url(r'^prepare/(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        PrepareTransmittalView.as_view(),
        name="transmittal_prepare"),
    url(r'^create/(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        CreateTransmittalView.as_view(),
        name="transmittal_create"),
    url(r'^incoming/$',
        TransmittalListView.as_view(),
        name="transmittal_list"),
    url(r'^incoming/(?P<transmittal_pk>\d+)/(?P<document_key>[\w-]+)/$',
        TransmittalDiffView.as_view(),
        name='transmittal_diff'),
    url(r'^incoming/(?P<transmittal_pk>\d+)/(?P<document_key>[\w-]+)/download/$',
        TransmittalDownloadView.as_view(),
        name='transmittal_download'),
    url(r'^incoming/(?P<transmittal_pk>\d+)/(?P<document_key>[\w-]+)/(?P<revision_document_key>[\w-]+)/(?P<revision>\d+)/$',
        TransmittalRevisionDiffView.as_view(),
        name='transmittal_revision_diff'),
)
