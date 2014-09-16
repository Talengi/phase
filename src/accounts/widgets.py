from django.core.urlresolvers import reverse

from restapi.widgets import AutocompleteTextInput


class BaseUserAutocomplete(AutocompleteTextInput):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({
            'data-value-field': 'id',
            'data-label-field': 'name',
            'data-search-fields': '["name"]',
            'data-url': reverse('user-list'),
        })
        super(BaseUserAutocomplete, self).__init__(attrs)


class UserAutocomplete(BaseUserAutocomplete):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({
            'data-mode': 'single',
        })
        super(UserAutocomplete, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value:
            obj = self.choices.queryset.get(pk=value)
            attrs.update({
                'data-initial-id': value,
                'data-initial-label': unicode(obj),
            })
        else:
            attrs.update({
                'data-initial-id': '',
                'data-initial-label': '',
            })
        return super(AutocompleteTextInput, self).render(name, value, attrs)


class MultipleUserAutocomplete(BaseUserAutocomplete):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({
            'data-mode': 'multi',
        })
        super(MultipleUserAutocomplete, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        value = value or []
        objects = self.choices.queryset.filter(pk__in=value)
        attrs.update({
            'data-initial-id': '[%s]' % ','.join(unicode(val) for val in value),
            'data-initial-label': '[%s]' % ','.join('"%s"' % obj for obj in objects),
        })
        return super(AutocompleteTextInput, self).render(name, value, attrs)
