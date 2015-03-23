# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.views.generic import TemplateView, ListView, DetailView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from braces.views import LoginRequiredMixin

from notifications.models import notify
from transmittals.models import Transmittal, TrsRevision
from transmittals.utils import FieldWrapper


logger = logging.getLogger(__name__)


class TransmittalListView(LoginRequiredMixin, ListView):
    """List all transmittals."""
    context_object_name = 'transmittal_list'

    def breadcrumb_section(self):
        return (_('Transmittals'), reverse('transmittal_list'))

    def get_queryset(self):
        # TODO
        # - Does anyone has the right to view every transmittals?
        # - Configure ACLs
        return Transmittal.objects.order_by('-id').all()


class TransmittalDiffView(LoginRequiredMixin, DetailView):
    template_name = 'transmittals/diff_view.html'
    context_object_name = 'transmittal'

    def breadcrumb_section(self):
        return (_('Transmittals'), reverse('transmittal_list'))

    def breadcrumb_object(self):
        return self.object

    def get_object(self, queryset=None):
        qs = Transmittal.objects \
            .filter(pk=self.kwargs['transmittal_pk']) \
            .filter(transmittal_key=self.kwargs['transmittal_key'])
        return qs.get()

    def get_context_data(self, **kwargs):
        context = super(TransmittalDiffView, self).get_context_data(**kwargs)
        context.update({
            'revisions': self.object.trsrevision_set.all()
        })

        return context

    def post(self, request, *args, **kwargs):
        """Accept or reject transmittal."""
        self.object = self.get_object()
        action = request.POST.get('action', None)

        if action == 'reject':
            method = getattr(self.object, 'reject')
            success_msg = 'The transmittal {} was sucessfully rejected.'.format(
                self.object)
            error_msg = 'We failed to process rejection of transmittal {}. ' \
                        'Please contact an administrator.'.format(self.object)
        elif action == 'accept':
            method = getattr(self.object, 'accept')
            success_msg = 'The transmittal {} is currently being processed.'.format(
                self.object)
            error_msg = 'We failed to process the import of transmittal {}. ' \
                        'Please contact an administrator.'.format(self.object)

        try:
            method()
            notify(request.user, success_msg)
            return HttpResponseRedirect(reverse('transmittal_list'))
        except Exception as e:
            error_msg = '{} ({})'.format(error_msg, e)
            notify(request.user, error_msg)
            logger.error(e)
            return HttpResponseRedirect(self.object.get_absolute_url())


class TransmittalRevisionDiffView(LoginRequiredMixin, DetailView):
    template_name = 'transmittals/revision_diff_view.html'
    context_object_name = 'trs_revision'

    def breadcrumb_section(self):
        return (_('Transmittals'), reverse('transmittal_list'))

    def breadcrumb_subsection(self):
        return self.object.transmittal

    def breadcrumb_object(self):
        return self.object

    def get_object(self, queryset=None):
        qs = TrsRevision.objects \
            .filter(transmittal__pk=self.kwargs['transmittal_pk']) \
            .filter(transmittal__transmittal_key=self.kwargs['transmittal_key']) \
            .filter(document_key=self.kwargs['document_key']) \
            .filter(revision=self.kwargs['revision']) \
            .select_related('transmittal', 'document', 'document__category',
                            'document__category__organisation',
                            'document__category__category_template')
        try:
            obj = qs.get()
        except(qs.model.DoesNotExist):
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': qs.model._meta.verbose_name})

        return obj

    def get_revision(self):
        """Get the revision to compare the imported data to.

        Three different cases:

         - if we are modifying an existing revision, get this revision
         - if we are creating a new revision and the previous revisions exists,
           get this previous revision.
         - if we are creating a new revision and the previous revision will
           also be created, get the corresponding trs line.

        """
        trs_revision = self.object
        document = trs_revision.document
        metadata = document.metadata
        latest_revision = document.current_revision

        # existing revision
        if trs_revision.revision <= latest_revision:
            revision = FieldWrapper((
                metadata,
                metadata.get_revision(trs_revision.revision)))

        # next revision creation
        elif trs_revision.revision == latest_revision + 1:
            revision = FieldWrapper((
                metadata,
                metadata.latest_revision))

        # previous revision will also be created
        else:
            try:
                revision = TrsRevision.objects \
                    .filter(transmittal=trs_revision.transmittal) \
                    .filter(document_key=trs_revision.document_key) \
                    .filter(revision=trs_revision.revision - 1) \
                    .get()
            except TrsRevision.DoesNotExist():
                logger.error('No revision to compare to {} / {} /  {}'.format(
                    trs_revision.transmittal.transmittal_key,
                    trs_revision.document_key,
                    trs_revision.revision))
                revision = {}

        return revision

    def get_context_data(self, **kwargs):
        context = super(TransmittalRevisionDiffView, self).get_context_data(**kwargs)
        context.update({
            'revision': self.get_revision(),
        })
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.comment = request.POST.get('comment')
        accept = request.POST.get('accept', False)
        self.object.accepted = bool(accept)
        self.object.save()
        return HttpResponseRedirect(reverse(
            'transmittal_diff',
            args=[self.object.transmittal.pk,
                  self.object.transmittal.transmittal_key]))


class DemoDiffView(TemplateView):
    template_name = 'transmittals/demo_diff_view.html'

    def breadcrumb_section(self):
        return 'Transmittal'

    def breadcrumb_subsection(self):
        return 'FAC10005-CTR-CLT-TRS-00001'


class DemoRevisionDiffView(TemplateView):
    template_name = 'transmittals/demo_revision_diff_view.html'

    def breadcrumb_section(self):
        return 'Transmittal'

    def breadcrumb_subsection(self):
        return 'FAC10005-CTR-CLT-TRS-00001'
