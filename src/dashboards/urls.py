# -*- coding: utf-8 -*-



from django.conf.urls import url

from dashboards.views import DashboardView

urlpatterns = [
    url(r'^(?P<organisation>[\w-]+)/dashboards/(?P<dashboard>[\w-]+)/$',
        DashboardView.as_view(),
        name='dashboard_detail'),
]
