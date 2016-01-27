# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from reviews.models import DistributionList


class DistributionListAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('reviewers',)


admin.site.register(DistributionList, DistributionListAdmin)
