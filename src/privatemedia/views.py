# -*- coding: utf-8 -*-


import os
from os.path import basename, join
try:
    from urllib.parse import unquote
except ImportError:
    from urllib.parse import unquote

from django.http import Http404, HttpResponse
from django.http.request import HttpRequest
from django.core.exceptions import ImproperlyConfigured
from django.views.static import serve
from django.views.generic import View
from django.conf import settings

from braces.views import LoginRequiredMixin


def serve_model_file_field(model, field_name):
    """Serves a protected / private media file."""
    # Does the class has such a field name?
    if not hasattr(model, field_name):
        raise Http404('There is no such field')

    # Is there an actual file associated to it?
    field = getattr(model, field_name)
    if not field:
        raise Http404('No file to download')

    storage = field.storage
    xaccel_prefix = getattr(storage, 'xaccel_prefix', None)
    if xaccel_prefix is None:
        raise ImproperlyConfigured("Use Phase's custom storage classes")

    if settings.USE_X_SENDFILE:
        file_name = basename(field.name)
        xaccel_url = join(xaccel_prefix, field.name)
        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        response['Content-Type'] = ''
        response['X-Accel-Redirect'] = xaccel_url
        return response
    else:
        request = HttpRequest()
        root = storage.location
        return serve(request, field.name, document_root=root)


class ProtectedDownload(LoginRequiredMixin, View):
    """Serve files with a web server after an ACL control.

    One might consider some alternate way, like this one:
    https://github.com/johnsensible/django-sendfile

    TODO Replace with django-downloadview

    """

    def get(self, request, *args, **kwargs):
        file_path = kwargs.get('file_path')

        # Prevent nasty things to happen
        clean_path = os.path.normpath(unquote(file_path))
        if clean_path.startswith('/') or '..' in clean_path:
            raise Http404('Nice try!')

        full_path = os.path.join(
            settings.PROTECTED_ROOT,
            clean_path)

        if not os.path.exists(full_path):
            raise Http404('File not found. Check the name.')

        # The X-sendfile Apache module makes it possible to serve file
        # directly from apache, but keeping a control from Django.
        # If we are in debug mode, and the module is unavailable, we fallback
        # to the django internal method to serve static files
        if settings.USE_X_SENDFILE:
            file_url = os.path.join(
                settings.PROTECTED_X_ACCEL_PREFIX,
                clean_path)
            file_name = os.path.basename(clean_path)

            response = HttpResponse(content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name
            response['Content-Type'] = ''  # Apache will guess this
            response['X-Sendfile'] = full_path
            response['X-Accel-Redirect '] = file_url
            return response
        else:
            return serve(request, full_path, document_root=settings.PROTECTED_ROOT)
