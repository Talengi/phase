from django.core.urlresolvers import reverse

from restapi.widgets import AutocompleteTextInput


class BaseUserAutocomplete(AutocompleteTextInput):

    def set_category(self, category):
        self.attrs.update({
            'data-value-field': 'id',
            'data-label-field': 'name',
            'data-search-fields': '["name"]',
            'data-url': reverse('user-list', args=[
                category.organisation.slug,
                category.category_template.slug])})


class UserAutocomplete(BaseUserAutocomplete):

    def set_category(self, category):
        super(UserAutocomplete, self).set_category(category)
        self.attrs.update({
            'data-mode': 'single',
        })

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
    def set_category(self, category):
        super(MultipleUserAutocomplete, self).set_category(category)
        self.attrs.update({
            'data-mode': 'multi',
        })

    def render(self, name, value, attrs=None):
        value = value or []
        import pdb; pdb.set_trace()
        objects = self.choices.queryset.filter(pk__in=value)
        attrs.update({
            'data-initial-id': '[%s]' % ','.join(unicode(val) for val in value),
            'data-initial-label': '[%s]' % ','.join('"%s"' % obj for obj in objects),
        })
        return super(AutocompleteTextInput, self).render(name, value, attrs)
