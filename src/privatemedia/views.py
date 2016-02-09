# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import basename, join

from django.http import Http404, HttpResponse
from django.core.exceptions import ImproperlyConfigured
from django.contrib.staticfiles.views import serve
from django.test import RequestFactory
from django.conf import settings


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

    file_name = basename(field.name)
    xaccel_url = join(xaccel_prefix, field.name)

    if settings.USE_X_SENDFILE:
        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        response['Content-Type'] = ''
        response['X-Accel-Redirect'] = xaccel_url
        return response
    else:
        request = RequestFactory()
        return serve(request, field.path)
