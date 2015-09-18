# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from exports.views import ExportCreate, ExportList, DownloadView


urlpatterns = patterns(
    '',

    url(r'^$',
        ExportList.as_view(),
        name="export_list"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        ExportCreate.as_view(),
        name="export_create"),
    url(r'^(?P<filename>[-\w]+\.[\w]{3,4})$',
        DownloadView.as_view(),
        name='export_download')
)
