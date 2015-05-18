from os.path import basename

from django.forms.widgets import ClearableFileInput
from django.utils.html import conditional_escape, format_html
from django.utils.encoding import force_text
from django.forms.widgets import CheckboxInput
from django.utils.safestring import mark_safe
from django.template.defaultfilters import filesizeformat


class PhaseClearableFileInput(ClearableFileInput):
    """Better file input widget.

    We update the template to suit our needs. Widget behavior does not
    change otherwise.

    """
    url_markup_template = u'<a href="{0}">{1}</a> ({2})'
    template_with_initial = u'<div class="fileinput">%(initial)s %(clear_template)s<br /><div class="change">%(input_text)s: %(input)s</div></div>'
    template_with_clear = u'<div class="clear">%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label></div>'

    def render(self, name, value, attrs=None):
        """Render the field.

        We want to only display the initial file basename. It seems there is no
        other way to do it than to rewrite this method entirely.

        """
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            filename = basename(force_text(value))
            try:
                filesize = filesizeformat(value.size)
            except OSError:
                filesize = 'NA'
            substitutions['initial'] = format_html(
                self.url_markup_template,
                value.url,
                filename,
                filesize)
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)
