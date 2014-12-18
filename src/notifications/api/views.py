# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.authentication import SessionAuthentication

from notifications.models import Notification
from notifications.api.serializers import NotificationSerializer


# See https://github.com/tomchristie/django-rest-framework/issues/1588
class NoCSRFAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    model = Notification
    serializer_class = NotificationSerializer
    paginate_by = settings.API_PAGINATE_BY
    paginate_by_param = 'page_limit'
    authentication_classes = (NoCSRFAuthentication,)

    def get_queryset(self):
        return Notification.objects \
            .filter(user=self.request.user) \
            .order_by('-created_on')

    @list_route(methods=['post'])
    def mark_as_read(self, request):
        qs = self.get_queryset()
        qs.update(seen=True)
        return Response({'status': 'done'})
