from django.forms.models import ModelChoiceField, ModelMultipleChoiceField

from api.widgets import UserAutocomplete, MultipleUserAutocomplete
from accounts.models import User


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
