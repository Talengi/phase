# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import admin

from dashboards.models import Dashboard


class DashboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'data_provider')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Dashboard, DashboardAdmin)
