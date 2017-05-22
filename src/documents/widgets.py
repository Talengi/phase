# -*- coding: utf-8 -*-


from os.path import basename

from django.forms.widgets import ClearableFileInput
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.template.defaultfilters import filesizeformat


class RevisionClearableFileInput(ClearableFileInput):
    template_with_initial = (
        '<div class="fileinput">'
        '   <a href="%(initial_url)s">%(initial)s</a> <br />'
        '   <div class="clear">'
        '      %(clear_template)s<br />'
        '   </div>'
        '   <div class="change">'
        '       %(input_text)s: %(input)s'
        '   </div>'
        '</div>'
    )

    def get_template_substitution_values(self, value):
        """Return value-related substitutions."""
        filename = basename(force_text(value))
        try:
            filesize = filesizeformat(value.size)
        except OSError:
            filesize = 'NA'
        text = '{} ({})'.format(filename, filesize)

        # This value could be set in the top form
        if hasattr(self, 'value_url'):
            url = self.value_url
        else:
            url = value.url

        return {
            'initial': text,
            'initial_url': conditional_escape(url),
        }
