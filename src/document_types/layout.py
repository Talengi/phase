"""Custom crispy forms layouts for document forms.

See https://django-crispy-forms.readthedocs.org/en/d-0/layouts.html

"""

from django.template.loader import render_to_string
from django.template import Context
from django.utils.text import slugify
from crispy_forms.layout import LayoutObject, Fieldset
from crispy_forms.utils import render_field


class ScheduleStatusLayout(LayoutObject):
    """Render a single line of the schedule table."""
    template = 'layout/schedule_status.html'
    field_template = 'layout/schedule_status_field.html'

    def __init__(self, name, **kwargs):
        self.name = name

    def render(self, form, form_style, context):
        planned_field = form['status_%s_planned_date' % self.name]
        forecast_field = form['status_%s_forecast_date' % self.name]
        actual_field = form['status_%s_actual_date' % self.name]

        planned = render_to_string(
            self.field_template,
            Context({
                'field': planned_field,
                'form_style': form_style,
            }))

        forecast = render_to_string(
            self.field_template,
            Context({
                'field': forecast_field,
                'form_style': form_style,
            }))

        actual = render_to_string(
            self.field_template,
            Context({
                'field': actual_field,
                'form_style': form_style,
            }))

        return render_to_string(
            self.template,
            Context({
                'form_style': form_style,
                'name': self.name,
                'planned_field': planned,
                'forecast_field': forecast,
                'actual_field': actual,
            }))


class ScheduleLayout(LayoutObject):
    """Rendel the whole schedule table."""
    template = 'layout/schedule.html'

    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)

    def render(self, form, form_style, context):
        fields = [render_field(field, form, form_style, context) for field in self.fields]

        return render_to_string(
            self.template,
            Context({
                'fields': ' '.join(fields),
                'form_style': form_style,
            }))


class FlatRelatedDocumentsLayout(LayoutObject):
    template = 'layout/related_documents_list.html'

    def __init__(self, field):
        self.field = field

    def render(self, form, form_style, context, template_pack=None):
        documents = form.instance.related_documents.all()

        return render_to_string(
            self.template,
            Context({
                'documents': documents,
                'form_style': form_style,
            }))


class DocumentFieldset(Fieldset):
    """We need to overload this class to always add a default id attribute."""

    def __init__(self, *args, **kwargs):
        super(DocumentFieldset, self).__init__(*args, **kwargs)
        if self.css_id is None:
            legend = unicode(self.legend)
            self.css_id = 'fieldset-%s' % slugify(legend)
