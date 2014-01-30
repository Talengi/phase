from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.utils import DatabaseError


def get_choices_from_list(list_index):
    """Creates a list of values from data in db."""
    from .models import ListEntry
    try:
        values = ListEntry.objects \
            .filter(values_list__index=list_index) \
            .values_list('index', 'value')

        # Execute query now, so we can catch any database error
        # For example if db does not exists, and we are trying to
        # run manage.py syncdb
        values = list(values)
    except DatabaseError:
        values = None

    return values


class ConfigurableChoiceField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.list_index = kwargs.pop('list_index', None)
        if self.list_index is None:
            raise ImproperlyConfigured('Missing field: list_index')
        defaults = {
            'max_length': 50,
            'choices': None,
        }
        defaults.update(kwargs)
        super(ConfigurableChoiceField, self).__init__(*args, **defaults)

    def _get_choices(self):
        if self._choices == []:
            choices = get_choices_from_list(self.list_index)
            if choices is None:
                return BLANK_CHOICE_DASH
            else:
                self._choices = choices
        return self._choices
    choices = property(_get_choices)
