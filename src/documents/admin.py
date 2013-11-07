from django.contrib import admin

from .models import CategoryTemplate
from .admin_forms import CategoryTemplateAdminForm


class CategoryTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    form = CategoryTemplateAdminForm


admin.site.register(CategoryTemplate, CategoryTemplateAdmin)
