from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as django_UserAdmin
from django.contrib.auth.admin import GroupAdmin as django_GroupAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from .models import User, Organisation, Category
from .forms import UserCreationForm, UserChangeForm


#class CategoryInline(admin.StackedInline):
#    model = CategoryMembership
#    fields = ('category',)
#    extra = 0


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    #inlines = [CategoryInline]
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description')}),
    )


class RequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(RequiredInlineFormSet, self).clean()

        existing_data = [data and not data.get('DELETE', False)
                         for data in self.cleaned_data]
        if not any(existing_data):
            raise forms.ValidationError(_('Please select at least one category'))


#class UserCategoryInline(admin.StackedInline):
#    model = CategoryMembership.users.through
#    extra = 0
#    formset = RequiredInlineFormSet


class UserAdmin(django_UserAdmin):
    """User admin module.

    Inspired by :
    https://docs.djangoproject.com/en/1.5/topics/auth/customizing/#a-full-example

    """
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
    #inlines = [UserCategoryInline]

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
        ('Permissions', {'fields': ('groups', 'user_permissions',)}),
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
    filter_horizontal = ('user_permissions', 'groups',)

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


class GroupAdminForm(forms.ModelForm):
    """Custom Group form for admin module.

    We use a custom form so we can add a widget to set users directly
    from the group admin module.

    """
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=FilteredSelectMultiple('Users', False),
        required=False)

    class Meta:
        model = Group

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            initial = kwargs.get('initial', {})
            initial['users'] = instance.user_set.all()
            kwargs['initial'] = initial
        super(GroupAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        group = super(GroupAdminForm, self).save(commit=commit)

        if commit:
            group.user_set = self.cleaned_data['users']
        else:
            old_save_m2m = self.save_m2m

            def new_save_m2m():
                old_save_m2m()
                group.user_set = self.cleaned_data['users']
            self.save_m2m = new_save_m2m
        return group


#class GroupCategoryInline(admin.StackedInline):
#    model = CategoryMembership.groups.through
#    extra = 0


class GroupAdmin(django_GroupAdmin):
    form = GroupAdminForm
    #inlines = [GroupCategoryInline]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('organisation', 'category_template')
    search_fields = ('organisation__name', 'category_template__name')
    filter_horizontal = ('users', 'groups')
    fieldsets = (
        (None, {'fields': ('organisation', 'category_template')}),
        ('Members', {'fields': ('groups', 'users',)}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.register(Category, CategoryAdmin)
