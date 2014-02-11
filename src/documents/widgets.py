from django.forms.widgets import ClearableFileInput


class PhaseClearableFileInput(ClearableFileInput):
    """Better file input widget.

    We update the template to suit our needs. Widget behavior does not
    change otherwise.

    """
    template_with_initial = u'<div class="fileinput">%(initial)s %(clear_template)s<br /><div class="change">%(input_text)s: %(input)s</div></div>'
    template_with_clear = '<div class="clear">%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label></div>'
