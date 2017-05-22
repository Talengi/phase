# -*- coding: utf-8 -*-


from django.db.models import Q

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission

from restapi.views import CategoryAPIViewMixin
from accounts.models import User
from accounts.api.serializers import UserSerializer


class DCPermissions(BasePermission):
    perm = 'documents.can_control_document'

    def has_permission(self, request, view):
        return request.user.has_perm(self.perm)


class UserViewSet(CategoryAPIViewMixin, viewsets.ReadOnlyModelViewSet):
    model = User
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, DCPermissions)

    def get_queryset(self):
        qs = User.objects.filter(categories=self.get_category())

        q = self.request.query_params.get('q', None)
        if q:
            # Should we use an index?
            # See http://dba.stackexchange.com/a/21648/85866
            q_name = Q(name__icontains=q)
            q_email = Q(email__icontains=q)
            qs = qs.filter(q_name | q_email)

        return qs
