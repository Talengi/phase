from django.forms.widgets import Select


class AutocompleteTextInput(Select):
    class Media:
        css = {
            'all': ('css/selectize.css',)
        }
        js = ('js/selectize.js',)
