"""Custom crispy forms layouts for document forms.

See https://django-crispy-forms.readthedocs.org/en/d-0/layouts.html

"""
# -*- coding: utf-8 -*-



from django.template.loader import render_to_string
from django.template import Template
from django.utils.text import slugify

from crispy_forms.compatibility import text_type
from crispy_forms.layout import Field, LayoutObject, Fieldset, TEMPLATE_PACK
from crispy_forms.utils import render_field


class ScheduleStatusLayout(Field):
    """Render a single line of the schedule table."""
    template = 'layout/schedule_status.html'
    field_template = 'layout/schedule_status_field.html'

    def __init__(self, name, **kwargs):
        self.name = name
        super(ScheduleStatusLayout, self).__init__(name, **kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK,
               **kwargs):

        planned = render_field(
            'status_%s_planned_date' % self.name,
            form,
            form_style,
            context,
            attrs=self.attrs,
            template=self.field_template,
            **kwargs)

        forecast = render_field(
            'status_%s_forecast_date' % self.name,
            form,
            form_style,
            context,
            attrs=self.attrs,
            template=self.field_template,
            **kwargs)

        actual_attrs = self.attrs.copy()
        actual_attrs.update({'readonly': 'readonly'})
        actual = render_field(
            'status_%s_actual_date' % self.name,
            form,
            form_style,
            context,
            attrs=actual_attrs,
            template=self.field_template,
            **kwargs)

        return render_to_string(self.template, {
            'form_style': form_style,
            'name': self.name,
            'planned_field': planned,
            'forecast_field': forecast,
            'actual_field': actual,
        })


class ScheduleLayout(LayoutObject):
    """Rendel the whole schedule table."""
    template = 'layout/schedule.html'

    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        fields = [render_field(field, form, form_style, context) for field in self.fields]

        return render_to_string(self.template, {
            'fields': ' '.join(fields),
            'form_style': form_style,
        })


class FlatRelatedDocumentsLayout(LayoutObject):
    template = 'layout/related_documents_list.html'

    def __init__(self, field):
        self.field = field

    def render(self, form, form_style, context, template_pack=None):
        documents = form.instance.related_documents.all()

        return render_to_string(self.template, {
            'documents': documents,
            'form_style': form_style,
        })


class PropertyLayout(LayoutObject):
    """Display a text value as a fake readonly input."""

    html = '''
    <div id="" class="form-group{% if field.css_classes %} {{ field.css_classes }}{% endif %}">
        <div class="control-label">{{ name|safe }}</div>
        <div class="controls">
            <span class="uneditable-input" {{ flat_attrs|safe }}>{{ value }}</span>
        </div>
    </div>
    '''

    list_html = '''
     <div id="" class="form-group{% if field.css_classes %} {{ field.css_classes }}{% endif %}">
         <div class="control-label">{{ name|safe }}</div>
         <div class="controls">
             <ul>
                 {{ value|safe }}
             </ul>
         </div>
     </div>
     '''

    def __init__(self, name):
        self.property_name = name

    def render(self, form, form_style, context, template_pack=None):
        prop = getattr(form.instance, self.property_name) or ''
        prop_name = self.property_name

        try:
            form_field = form.fields[prop_name]
        except:
            form_field = None

        try:
            model_field = form.instance._meta.get_field(prop_name)
        except:
            model_field = None

        # Get the property label
        if hasattr(prop, 'short_description'):
            name = prop.short_description
        elif form_field:
            name = form_field.label
        elif model_field:
            name = model_field.verbose_name
        else:
            name = self.property_name

        # If the property is some kind of list
        iterator = None
        if isinstance(prop, (list, tuple)):
            iterator = prop
        elif prop.__class__.__name__ == 'ManyRelatedManager':
            iterator = prop.all()

        if iterator is not None:
            template = self.list_html
            value = '<li>%s</li>' % '</li><li>'.join([i for i in iterator])
        else:
            template = self.html
            value = prop

        context.update({
            'name': name,
            'value': value,
        })
        return Template(text_type(template)).render(context)


class YesNoLayout(PropertyLayout):

    html = '''
    <div id="" class="form-group{% if field.css_classes %} {{ field.css_classes }}{% endif %}">
        <div class="control-label">{{ name|safe }}</div>
        <div class="controls">
            <span class="uneditable-input" {{ flat_attrs|safe }}>{{ value|yesno:_("Yes,No") }}</span>
        </div>
    </div>
    '''


class UneditableFile(LayoutObject):
    existing_file_html = '''
    <div id="div_{{ field.auto_id }}" class="form-group{% if field.css_classes %} {{ field.css_classes }}{% endif %}">
        <label for="{{ field.id_for_label }}" class="control-label">
            {{ field.label|safe }}
        </label>
        <div class="controls">
            <a href="{{ url }}">{{ name }}</a>
        </div>
    </div>
    '''

    no_file_html = '''
    <div id="div_{{ field.auto_id }}" class="form-group{% if field.css_classes %} {{ field.css_classes }}{% endif %}">
        <label for="{{ field.id_for_label }}" class="control-label">
            {{ field.label|safe }}
        </label>
        <div class="controls">
            <span>There is no associated file</span>
        </div>
    </div>
    '''

    def __init__(self, *args, **kwargs):
        self.fields = list(args)

    def render(self, form, form_style, context, template_pack=None):
        field = form[self.fields[0]]
        value = field.value()
        try:
            html = self.existing_file_html
            name = value.name
            url = value.url
        except (ValueError, AttributeError):
            html = self.no_file_html
            name = None
            url = None

        context.update({
            'field': field,
            'name': name,
            'url': url,
        })

        field_name = self.fields[0]
        if field_name not in form.rendered_fields:
            form.rendered_fields.add(field_name)

        return Template(text_type(html)).render(context)


class DocumentFieldset(Fieldset):
    """We need to overload this class to always add a default id attribute."""

    def __init__(self, *args, **kwargs):
        super(DocumentFieldset, self).__init__(*args, **kwargs)
        if self.css_id is None:
            legend = self.legend
            self.css_id = 'fieldset-%s' % slugify(legend)


class DateField(Field):
    template = 'layout/date_field.html'

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        if hasattr(self, 'wrapper_class'):
            context['wrapper_class'] = self.wrapper_class

        if form.read_only:
            template = "%s/field.html" % TEMPLATE_PACK
        else:
            template = self.template

        html = ''
        for field in self.fields:
            html += render_field(field, form, form_style, context,
                                 template=template, attrs=self.attrs,
                                 template_pack=template_pack)
        return html
