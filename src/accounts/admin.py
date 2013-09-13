from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as django_UserAdmin

from .models import User
from .forms import UserCreationForm, UserChangeForm


class UserAdmin(django_UserAdmin):
    """User admin module.

    Inspired by :
    https://docs.djangoproject.com/en/1.5/topics/auth/customizing/#a-full-example

    """
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'position', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'position',)}),
        ('Permissions', {'fields': ('is_superuser',)}),
        ('Important dates', {'fields': ('date_joined', 'last_login',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')}),
    )
    search_fields = ('email', 'name', 'position')
    ordering = ('email',)
    filter_horizontal = ()


#admin.site.unregister(django_User, django_UserAdmin)
admin.site.register(User, UserAdmin)
