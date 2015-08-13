# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission

from categories.models import Category
from accounts.models import User
from accounts.api.serializers import UserSerializer


class DCPermissions(BasePermission):
    perm = 'documents.can_control_document'

    def has_permission(self, request, view):
        return request.user.has_perm(self.perm)


class CategoryPermission(BasePermission):

    def has_permission(self, request, view):
        category = view.get_category()
        if category is None:
            return False
        return request.user in category.users.all()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = User
    serializer_class = UserSerializer
    paginate_by_param = 'page_limit'
    permission_classes = (IsAuthenticated, DCPermissions, CategoryPermission)
    _category = None

    def get_category(self):
        if self._category is None:
            organisation_slug = self.kwargs.get('organisation')
            category_slug = self.kwargs.get('category')
            try:
                self._category = Category.objects.get(
                    organisation__slug=organisation_slug,
                    category_template__slug=category_slug)
            except Category.DoesNotExist:
                self._category = None

        return self._category

    def get_queryset(self):
        qs = User.objects.filter(categories=self.get_category())

        q = self.request.query_params.get('q', None)
        if q:
            q_name = Q(name__icontains=q)
            q_email = Q(email__icontains=q)
            qs = qs.filter(q_name | q_email)

        return qs
