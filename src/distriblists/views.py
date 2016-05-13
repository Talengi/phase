# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import FormView
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from braces.views import LoginRequiredMixin

from distriblists.forms import (
    DistributionListImportForm, DistributionListExportForm)
from distriblists.utils import (import_lists, export_lists,
                                export_review_members)


class BaseListExport(LoginRequiredMixin, FormView):
    form_class = DistributionListExportForm
    template_name = 'distriblists/export.html'
    model_admin = None

    def get_form_kwargs(self):
        kwargs = super(BaseListExport, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'categories': self.request.user_categories
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BaseListExport, self).get_context_data(**kwargs)
        context.update(self.model_admin.admin_site.each_context(self.request))
        context.update({
            'title': self.page_title,
            'opts': self.model_admin.model._meta,
            'download_button_label': self.form_button_label,
        })
        return context


class ReviewMembersExport(BaseListExport):
    page_title = _('Export review members')
    form_button_label = _('Export review members')

    def get_success_url(self):
        return reverse('admin:distriblists_reviewmembers_export')

    def form_valid(self, form):
        category = form.cleaned_data['category']
        exported_file = export_review_members(category)
        filename = 'review_members_{}_{}.xlsx'.format(
            category.organisation.slug,
            category.slug
        )

        response = HttpResponse(
            exported_file,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        return response


class DistributionListImport(LoginRequiredMixin, FormView):
    form_class = DistributionListImportForm
    template_name = 'distriblists/import.html'
    model_admin = None

    def get_form_kwargs(self):
        kwargs = super(DistributionListImport, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'categories': self.request.user_categories
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DistributionListImport, self).get_context_data(**kwargs)
        context.update(self.model_admin.admin_site.each_context(self.request))
        context.update({
            'title': _('Import distribution lists'),
            'opts': self.model_admin.model._meta,
        })
        return context

    def get_success_url(self):
        return reverse('admin:distriblists_distriblist_import')

    def form_valid(self, form):
        category = form.cleaned_data['category']
        xls_file = form.files['xls_file']

        context = self.get_context_data(form=form)
        try:
            results = import_lists(xls_file, category)
            context.update({
                'results': results
            })
        except:
            # Any error occurred, file must be inparsable
            error_msg = _("We could'nt parse your file. Is this a valid xlsx file?")
            context.update({
                'non_form_errors': error_msg
            })

        return self.render_to_response(context)


class DistributionListExport(BaseListExport):
    page_title = _('Export distribution lists')
    form_button_label = _('Export distribution lists')

    def get_success_url(self):
        return reverse('admin:distriblists_distriblist_export')

    def form_valid(self, form):
        category = form.cleaned_data['category']
        exported_file = export_lists(category)
        filename = 'lists_{}_{}.xlsx'.format(
            category.organisation.slug,
            category.slug
        )

        response = HttpResponse(
            exported_file,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        return response
