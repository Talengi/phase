from django.views.generic import CreateView

from imports.forms import FileUploadForm


class FileUpload(CreateView):
    template_name = 'imports/upload_file.html'
    form_class = FileUploadForm
