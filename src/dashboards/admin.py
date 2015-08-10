# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import admin

from dashboards.models import Dashboard


class DashboardAdmin(admin.ModelAdmin):
    pass


admin.site.register(Dashboard, DashboardAdmin)
