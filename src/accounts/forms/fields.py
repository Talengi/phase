# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.models import ModelChoiceField, ModelMultipleChoiceField

from accounts.forms.widgets import UserAutocomplete, MultipleUserAutocomplete


__all__ = ['UserChoiceField', 'UserMultipleChoiceField']


class UserChoiceField(ModelChoiceField):
    widget = UserAutocomplete

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        users = self.category.users.all()
        super(UserChoiceField, self).__init__(users, *args, **kwargs)
        self.widget.set_category(self.category)


class UserMultipleChoiceField(ModelMultipleChoiceField):
    widget = MultipleUserAutocomplete

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        users = self.category.users.all()
        super(UserMultipleChoiceField, self).__init__(users, *args, **kwargs)
        self.widget.set_category(self.category)

    def bound_data(self, value, initial):
        value = value.split(',') if value else value
        return value

    def clean(self, value):
        value = value.split(',') if value else value
        return super(UserMultipleChoiceField, self).clean(value)
