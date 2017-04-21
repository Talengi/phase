# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics

from restapi.views import CategoryAPIViewMixin
from distriblists.models import DistributionList
from distriblists.api.serializers import DistributionListSerializer


class DistributionListList(CategoryAPIViewMixin, generics.ListAPIView):
    model = DistributionList
    serializer_class = DistributionListSerializer

    def get_queryset(self):
        qs = DistributionList.objects \
            .filter(categories=self.get_category()) \
            .select_related('leader', 'approver') \
            .prefetch_related('reviewers')

        q = self.request.query_params.get('q', None)
        if q:
            # Should we use an index?
            # See http://dba.stackexchange.com/a/21648/85866
            qs = qs.filter(name__icontains=q)

        return qs
