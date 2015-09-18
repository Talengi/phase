# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.views.generic import ListView, UpdateView, View
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.views.static import serve
from django.shortcuts import get_object_or_404
from django.conf import settings

from braces.views import LoginRequiredMixin

from exports.models import Export
from documents.views import DocumentListMixin


class ExportCreate(LoginRequiredMixin, DocumentListMixin, UpdateView):
    """Request a new document list export.

    Note that even though this view is only used to create
    a new export, we inherit from `UpdateView` because we
    want to initialize the default instance ourselves in
    the `get_object` method.

    """

    model = Export
    fields = ('querystring',)
    http_method_names = ['post']

    def breadcrumb_section(self):
        return (_('Export'), '#')

    def get_form_kwargs(self):
        qd = self.request.POST.copy()
        qd.pop('csrfmiddlewaretoken')
        qd.pop('start')
        qd.pop('size')
        qd.pop('sort_by')

        kwargs = super(ExportCreate, self).get_form_kwargs()
        kwargs.update({'data': {
            'querystring': qd.urlencode()
        }})
        return kwargs

    def get_object(self):
        self.get_queryset()
        export = Export(
            owner=self.request.user,
            category=self.category)
        return export

    def get_success_url(self):
        return reverse('export_list')

    def form_valid(self, form):
        return_value = super(ExportCreate, self).form_valid(form)
        self.object.start_export()
        return return_value


class ExportList(LoginRequiredMixin, ListView):
    model = Export

    def breadcrumb_section(self):
        return (_('Exports'), reverse('export_list'))

    def get_queryset(self):
        return super(ExportList, self).get_queryset() \
            .filter(owner=self.request.user) \
            .select_related() \
            .order_by('-created_on')


class DownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        filename = kwargs.get('filename')
        name, ext = os.path.splitext(filename)

        _, _, uid = name.split('_')

        qs = Export.objects.filter(owner=self.request.user)
        export = get_object_or_404(qs, id=uid)

        filepath = export.get_filepath()
        if not os.path.exists(filepath):
            raise Http404()

        url = export.get_url()
        if settings.USE_X_SENDFILE:
            url = url.replace('/private/', settings.NGING_X_ACCEL_PREFIX)
            response = HttpResponse(content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            response['X-Accel-Redirect '] = url
            return response
        else:
            return serve(request, url, settings.PRIVATE_ROOT)
