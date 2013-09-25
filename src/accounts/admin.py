from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as django_UserAdmin
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages

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
        ('Permissions', {'fields': ('groups',)}),
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
    filter_horizontal = ('groups',)

    def save_model(self, request, obj, form, change):
        """Send account activation mail after user creation.

        We only send activation mail when the new user was created from
        the admin. We could have used a post_save signal, but we would have
        lost the ability to create a user without generating an email.

        """
        obj.save()
        if not change:
            token = default_token_generator.make_token(obj)
            obj.send_account_activation_email(token)
            messages.info(request, 'The account activation mail was sent')


#admin.site.unregister(django_User, django_UserAdmin)
admin.site.register(User, UserAdmin)
