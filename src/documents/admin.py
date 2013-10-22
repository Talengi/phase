from django.contrib import admin

from accounts.models import CategoryMembership
from .models import Category


class OrganisationInline(admin.TabularInline):
    model = CategoryMembership
    fields = ('organisation',)
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = [OrganisationInline]



admin.site.register(Category, CategoryAdmin)
