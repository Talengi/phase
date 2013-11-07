from django.contrib import admin

from .models import ValuesList, ListEntry, ContractorDeliverable


class EntryInline(admin.TabularInline):
    model = ListEntry
    extra = 10


class ValuesListAdmin(admin.ModelAdmin):
    list_display = ('index', 'name',)
    inlines = [EntryInline]


admin.site.register(ValuesList, ValuesListAdmin)
admin.site.register(ContractorDeliverable)
