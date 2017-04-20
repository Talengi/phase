# -*- coding: utf-8 -*-

from django.conf.urls import url

from distriblists.api.views import DistributionListList  # Yes, a list of lists


urlpatterns = [
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        DistributionListList.as_view(),
        name='distributionlist-list'),
]
