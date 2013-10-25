from django.contrib import admin

from documents.models import CategoryTemplate


class CategoryTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(CategoryTemplate, CategoryTemplateAdmin)
