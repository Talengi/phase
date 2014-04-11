from django.forms.widgets import TextInput


class AutocompleteTextInput(TextInput):
    class Media:
        css = {
            'all': ('css/selectize.css',)
        }
        js = ('js/selectize.js',)
