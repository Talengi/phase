# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from reviews.api.views import DistributionListList  # Yes, a list of lists


urlpatterns = patterns(
    '',
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        DistributionListList.as_view(),
        name='distributionlist-list'),
)
