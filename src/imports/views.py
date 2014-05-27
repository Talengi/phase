from django.views.generic import CreateView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from imports.forms import FileUploadForm


class FileUpload(CreateView):
    template_name = 'imports/upload_file.html'
    form_class = FileUploadForm

    def breadcrumb_section(self):
        return _('Import file'), reverse('import')
