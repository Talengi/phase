from django.forms.models import ModelChoiceField, ModelMultipleChoiceField

from accounts.widgets import UserAutocomplete, MultipleUserAutocomplete


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

    def clean(self, value):
        value = value.split(',') if value else value
        return super(UserMultipleChoiceField, self).clean(value)
