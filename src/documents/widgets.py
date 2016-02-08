# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

        return {
            'initial': text,
            'initial_url': conditional_escape(value.url),
        }
