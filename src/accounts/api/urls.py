# -*- coding: utf-8 -*-

from django.conf.urls import url

from accounts.api.views import UserViewSet

user_list = UserViewSet.as_view({
    'get': 'list',
})
user_detail = UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


urlpatterns = [
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$', user_list, name='user-list'),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?P<pk>\d+)/$',
        user_detail, name='user-detail'),
]
