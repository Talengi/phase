from __future__ import unicode_literals

from django.views.generic import CreateView, DetailView, ListView, FormView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin

from categories.models import Category
from notifications.models import notify
from imports.models import ImportBatch
from imports.forms import FileUploadForm, ImportTemplateGenerationForm
from imports.tasks import do_import
from utils import make_csv_template, make_xlsx_template


class ImportMixin(object):

    def breadcrumb_section(self):
        return _('Import'), reverse('import_list')

    def get_context_data(self, **kwargs):
        context = super(ImportMixin, self).get_context_data(**kwargs)
        context.update({
            'imports_active': True,
        })
        return context


class ImportList(ImportMixin, LoginRequiredMixin, ListView):
    template_name = 'imports/import_list.html'
    model = ImportBatch


class FileUpload(ImportMixin, LoginRequiredMixin, CreateView):
    template_name = 'imports/upload_file.html'
    form_class = FileUploadForm

    def breadcrumb_object(self):
        return _('Upload file'), reverse('import_file')

    def form_valid(self, form):
        response = super(FileUpload, self).form_valid(form)
        do_import.delay(self.object.uid)

        message_text = '''You required the import of a new file. Results
                       <a href="%(url)s">should be available in a few
                       seconds.</a>'''
        message_data = {
            'url': self.object.get_absolute_url(),
        }
        notify(self.request.user, _(message_text) % message_data)
        return response


class ImportStatus(ImportMixin, LoginRequiredMixin, DetailView):
    model = ImportBatch
    pk_url_kwarg = 'uid'
    template_name = 'imports/import_status.html'

    def breadcrumb_object(self):
        return self.object

    def get_context_data(self, **kwargs):
        context = super(ImportStatus, self).get_context_data(**kwargs)

        return context


class ImportTemplate(ImportMixin, LoginRequiredMixin, FormView):
    """Renders a csv template which header is populated with PhaseConfig
    import fields """

    template_name = 'imports/csv_template_generation.html'
    form_class = ImportTemplateGenerationForm

    def breadcrumb_object(self):
        return _('Import templates'), reverse('import_template')

    def get_success_url(self):
        """Avoiding circular imports caused by writing `success_url`"""
        return reverse('import_template')

    def get_template_maker(self):
        if 'format_csv' in self.request.POST.keys():
            return make_csv_template
        return make_xlsx_template

    def form_valid(self, form):
        response = super(ImportTemplate, self).form_valid(form)
        category_pk = form.cleaned_data['category']
        category = Category.objects.get(pk=category_pk)
        model_class = category.category_template.metadata_model.model_class()
        config = getattr(model_class, 'PhaseConfig')
        import_fields = getattr(config, 'import_fields', None)
        if import_fields:
            filename = category.category_template.slug
            response = self.get_template_maker()(
                import_fields, filename=filename)
        return response
