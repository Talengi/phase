from django.forms.models import ModelChoiceField, ModelMultipleChoiceField

from accounts.models import User
from accounts.widgets import UserAutocomplete, MultipleUserAutocomplete


class UserChoiceField(ModelChoiceField):
    widget = UserAutocomplete

    def __init__(self, *args, **kwargs):
        qs = User.objects.all()
        super(UserChoiceField, self).__init__(qs, *args, **kwargs)


class UserMultipleChoiceField(ModelMultipleChoiceField):
    widget = MultipleUserAutocomplete

    def __init__(self, *args, **kwargs):
        qs = User.objects.all()
        super(UserMultipleChoiceField, self).__init__(qs, *args, **kwargs)

    def clean(self, value):
        value = value.split(',') if value else value
        return super(UserMultipleChoiceField, self).clean(value)
