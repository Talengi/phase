# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.widgets import ClearableFileInput


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
