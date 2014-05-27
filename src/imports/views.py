from __future__ import unicode_literals

from django.views.generic import CreateView, DetailView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from imports.models import ImportBatch
from imports.forms import FileUploadForm


class ImportMixin(object):

    def breadcrumb_section(self):
        return _('Import file'), reverse('import_file')

    def get_context_data(self, **kwargs):
        context = super(ImportMixin, self).get_context_data(**kwargs)
        context.update({
            'imports_active': True,
        })
        return context


class FileUpload(ImportMixin, CreateView):
    template_name = 'imports/upload_file.html'
    form_class = FileUploadForm


class ImportStatus(ImportMixin, DetailView):
    model = ImportBatch
    pk_url_kwarg = 'uid'
    template_name = 'imports/import_status.html'
