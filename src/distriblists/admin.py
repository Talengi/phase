# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from distriblists.models import DistributionList
from distriblists.forms import DistributionListForm


class DistributionListAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('reviewers', 'categories')
    form = DistributionListForm


admin.site.register(DistributionList, DistributionListAdmin)
