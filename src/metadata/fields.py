# -*- coding: utf-8 -*-


from django import forms
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.text import capfirst
from django.core.cache import cache

from metadata.handlers import populate_values_list_cache


def get_choices_from_list(list_index):
    """Load the values list from cache.

    Cache is populated in multiple places:

     - post-migrate signal handler
     - when admin form is submitted
     - using the `reload_metadata_cache` task

    """
    cache_key = 'values_list_{}'.format(list_index)

    if cache_key not in cache:

        # The only reason it would fail is because the
        # db is not ready. So we'll try again later.
        try:
            populate_values_list_cache()
        except:  # noqa
            pass

    values = cache.get(cache_key, [])
    return values


class ConfigurableChoiceField(models.CharField):
    """A CharField with a select widget.

    The widget values are taken from values lists (in cache, of course).

    BIG FAT WARNING. This feature was the origin of countless bugs since the
    begining of the project. The current version seems to be ok, but apply
    modifications with care.

    Basically, this field is just a ChoiceField with dynamic choices taken
    from db.

    We used to set choices in the `_get_choices` method, but that won't work
    for several reasons:

      - that method is called only when the server starts, so choices would not
        be updated correctly.
      - that method is called even when the database is not ready, causing
        django to crash in some cases.

    No we use the `get_choices` method, that is only called on form
    initialization to set the form field and form widget values. That method
    has to be called manually after the form __init__ method, though.

    """
    def __init__(self, *args, **kwargs):
        self.list_index = kwargs.pop('list_index', None)
        if self.list_index is None:
            raise ImproperlyConfigured('Missing field: list_index')
        defaults = {
            'max_length': 50,
        }
        defaults.update(kwargs)
        super(ConfigurableChoiceField, self).__init__(*args, **defaults)

    def formfield(self, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
        }
        if self.has_default():
            defaults['initial'] = self.get_default()

        include_blank = (self.blank or
                         not (self.has_default() or 'initial' in kwargs))
        defaults['choices'] = self.get_choices(include_blank=include_blank)
        defaults['coerce'] = self.to_python
        return forms.TypedChoiceField(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(ConfigurableChoiceField, self).deconstruct()
        kwargs['list_index'] = self.list_index
        return name, path, args, kwargs

    def get_choices(self, include_blank=True):
        choices = get_choices_from_list(self.list_index)

        if include_blank:
            choices = list(BLANK_CHOICE_DASH) + choices
        return choices
