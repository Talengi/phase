from django.core.urlresolvers import reverse
from django.forms.widgets import TextInput


class AutocompleteTextInput(TextInput):
    class Media:
        css = {
            'all': ('css/selectize.css',)
        }
        js = ('js/selectize.js',)

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({
            'data-autocomplete': '',
        })
        super(AutocompleteTextInput, self).__init__(attrs)


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
        obj = self.choices.queryset.get(pk=value)
        attrs.update({
            'data-initial-id': value,
            'data-initial-label': unicode(obj),
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
        objects = self.choices.queryset.filter(pk__in=value)
        attrs.update({
            'data-initial-id': '[%s]' % ','.join(unicode(val) for val in value),
            'data-initial-label': '[%s]' % ','.join('"%s"' % obj for obj in objects),
        })
        return super(AutocompleteTextInput, self).render(name, value, attrs)
