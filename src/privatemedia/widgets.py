# -*- coding: utf-8 -*-


from os.path import basename

from django.forms.widgets import ClearableFileInput
from django.utils.encoding import force_text
from django.template.defaultfilters import filesizeformat
from django.utils.html import conditional_escape


class PhaseClearableFileInput(ClearableFileInput):
    """Better file input widget.

    We update the template to suit our needs. Widget behavior does not
    change otherwise.

    """
    template_name = 'forms/widgets/phase_clearable_file_input.html'

    def get_context(self, name, value, attrs):
        filename = basename(force_text(value))
        try:
            filesize = filesizeformat(value.size)
        except:
            filesize = 'NA'
        file_name = '{} ({})'.format(filename, filesize)

        if hasattr(self, 'value_url'):
            file_url = self.value_url
        elif value and hasattr(value, 'url'):
            file_url = value.url
        else:
            file_url = ''

        context = super().get_context(name, value, attrs)
        context.update({
            'file_name': file_name,
            'file_url': conditional_escape(file_url),
        })
        return context
