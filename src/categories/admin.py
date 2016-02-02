# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Organisation, CategoryTemplate, Category, Contract
from .admin_forms import CategoryTemplateAdminForm


class CategoryInline(admin.StackedInline):
    model = Category
    fields = ('category_template',)
    extra = 0


class GroupCategoryInline(admin.StackedInline):
    model = Category.groups.through
    extra = 0


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigram', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CategoryInline]
    prepopulated_fields = {'slug': ('name',)}


class CategoryTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    form = CategoryTemplateAdminForm


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('organisation', 'category_template')
    list_display_links = ('category_template',)
    search_fields = ('organisation__name', 'category_template__name')
    ordering = ('organisation', 'category_template')
    filter_horizontal = ('users', 'groups', 'third_parties')
    fieldsets = (
        (None, {'fields': ('organisation', 'category_template')}),
        ('Members', {'fields': ('groups', 'users',)}),
        ('Third parties', {'fields': ('third_parties',)}),
    )


class RequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(RequiredInlineFormSet, self).clean()

        existing_data = [data and not data.get('DELETE', False)
                         for data in self.cleaned_data]
        if not any(existing_data):
            raise forms.ValidationError(_('Please select at least one category'))


class UserCategoryInline(admin.StackedInline):
    model = Category.users.through
    extra = 0
    formset = RequiredInlineFormSet


class ContractAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'get_associated_categories')

    def get_associated_categories(self, obj):
        categories = obj.categories.all()
        return ", ".join([c.name for c in categories])

    get_associated_categories.short_description = _('Categories')

admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(CategoryTemplate, CategoryTemplateAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Contract, ContractAdmin)
