from django.forms.widgets import TextInput


class AutocompleteTextInput(TextInput):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({
            'data-autocomplete': '',
        })
        super(AutocompleteTextInput, self).__init__(attrs)
