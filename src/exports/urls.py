# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from exports.views import ExportCreate


urlpatterns = patterns(
    '',

    # Favorites
    url(r'^$',
        ExportCreate.as_view(),
        name="export_create"),
)
