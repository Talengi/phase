# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.widgets import ClearableFileInput


class RevisionClearableFileInput(ClearableFileInput):
    template_with_initial = (
        '<a href="%(initial_url)s">%(initial)s</a><br />'
        '%(clear_template)s<br />%(input_text)s: %(input)s'
    )
    template_with_clear = (
        '<div class="clear">%(clear)s '
        '<label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'
        '</div>'
    )
