# -*- coding: utf-8 -*-


from django.contrib import admin

from dashboards.models import Dashboard


class DashboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'data_provider')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('authorized_users',)


admin.site.register(Dashboard, DashboardAdmin)
