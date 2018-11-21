import logging

from django.views.generic import ListView, DetailView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.utils import timezone
from django.shortcuts import get_object_or_404

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from zipview.views import BaseZipView
from annoying.functions import get_object_or_None

from categories.models import Category
from notifications.models import notify
from documents.views import BaseDocumentBatchActionView
from transmittals.models import Transmittal, TrsRevision
from transmittals.utils import FieldWrapper
from transmittals.tasks import do_create_transmittal
from search.utils import index_revisions
from documents.views import DocumentListMixin
from accounts.models import get_entities
from privatemedia.views import serve_model_file_field
from django.conf import settings


logger = logging.getLogger(__name__)


class TransmittalList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """List all transmittals."""
    context_object_name = 'transmittal_list'
    permission_required = 'documents.can_control_document'

    def breadcrumb_section(self):
        return _('Transmittals')

    def breadcrumb_subsection(self):
        return (_('Incoming'), reverse('transmittal_list'))

    def get_queryset(self):
        return Transmittal.objects \
            .filter(document__category__users=self.request.user) \
            .exclude(status='accepted') \
            .select_related('document__category__organisation',
                            'document__category__category_template') \
            .order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(TransmittalList, self).get_context_data(**kwargs)
        context.update({
            'transmittals_active': True,
        })
        return context


class TransmittalDiff(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = 'transmittals/diff_view.html'
    permission_required = 'documents.can_control_document'
    context_object_name = 'revisions'
    paginate_by = settings.PAGINATE_BY

    def breadcrumb_section(self):
        return (_('Transmittals'), reverse('transmittal_list'))

    def breadcrumb_object(self):
        return self.object

    def get_object(self, queryset=None):
        qs = Transmittal.objects \
            .filter(document__category__users=self.request.user) \
            .filter(pk=self.kwargs['transmittal_pk']) \
            .filter(document_key=self.kwargs['document_key'])
        return qs.get()

    def get_queryset(self):
        return self.object.trsrevision_set.all().order_by('created_on')

    def get_context_data(self, **kwargs):
        context = super(TransmittalDiff, self).get_context_data(**kwargs)
        context.update({
            'transmittal': self.object,
            'transmittals_active': True,
        })

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(TransmittalDiff, self).get(request, *args, **kwargs)

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
            return HttpResponseRedirect(reverse(
                'transmittal_diff',
                args=[self.object.pk,
                      self.object.document_key]))


class TransmittalRevisionDiff(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    template_name = 'transmittals/revision_diff_view.html'
    context_object_name = 'trs_revision'
    permission_required = 'documents.can_control_document'

    def breadcrumb_section(self):
        return (_('Transmittals'), reverse('transmittal_list'))

    def breadcrumb_subsection(self):
        return self.object.transmittal

    def breadcrumb_object(self):
        return self.object

    def get_object(self, queryset=None):
        qs = TrsRevision.objects \
            .filter(transmittal__document__category__users=self.request.user) \
            .filter(transmittal__pk=self.kwargs['transmittal_pk']) \
            .filter(transmittal__document_key=self.kwargs['document_key']) \
            .filter(document_key=self.kwargs['revision_document_key']) \
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

        Four different cases:

         - if we are creating a new document, we have nothing to compare to
         - if we are modifying an existing revision, get this revision
         - if we are creating a new revision and the previous revisions exists,
           get this previous revision.
         - if we are creating a new revision and the previous revision will
           also be created, get the corresponding trs line.

        """
        trs_revision = self.object
        document = trs_revision.document
        metadata = getattr(document, 'metadata', None)
        latest_revision = getattr(document, 'current_revision', 0)

        # No existing document, document + revision creation
        if document is None and trs_revision.revision == 0:
            revision = trs_revision

        # No existing document, but the previous revision will be created
        # before this one
        elif document is None and trs_revision.revision > 0:
            qs = TrsRevision.objects \
                .filter(transmittal=trs_revision.transmittal) \
                .filter(document_key=trs_revision.document_key) \
                .filter(revision=trs_revision.revision - 1)
            revision = get_object_or_None(qs)

        # existing revision
        elif trs_revision.revision <= latest_revision:
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
            qs = TrsRevision.objects \
                .filter(transmittal=trs_revision.transmittal) \
                .filter(document_key=trs_revision.document_key) \
                .filter(revision=trs_revision.revision - 1)
            revision = get_object_or_None(qs)

        if revision is None:
            logger.error('No revision to compare to {} / {} /  {}'.format(
                trs_revision.transmittal.document_key,
                trs_revision.document_key,
                trs_revision.revision))
            revision = {}

        return revision

    def get_context_data(self, **kwargs):
        context = super(TransmittalRevisionDiff, self).get_context_data(**kwargs)
        context.update({
            'revision': self.get_revision(),
            'transmittals_active': True,
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
                  self.object.transmittal.document_key]))


class TransmittalDownload(LoginRequiredMixin, PermissionRequiredMixin, BaseZipView):
    zipfile_name = 'transmittal_documents.zip'
    permission_required = 'documents.can_control_document'

    def get_files(self):
        transmittal_pk = self.kwargs.get('transmittal_pk')
        document_key = self.kwargs.get('document_key')
        revision_ids = self.request.GET.getlist('revision_ids')
        file_format = self.request.GET.get('format', 'both')

        revisions = TrsRevision.objects \
            .filter(transmittal__document__category__users=self.request.user) \
            .filter(transmittal__id=transmittal_pk) \
            .filter(transmittal__document_key=document_key) \
            .filter(id__in=revision_ids)

        files = []
        for revision in revisions:
            if file_format in ('pdf', 'both') and revision.pdf_file.name:
                files.append(revision.pdf_file.file)

            if file_format in ('native', 'both') and revision.native_file.name:
                files.append(revision.native_file.file)

        return files


class PrepareTransmittal(BaseDocumentBatchActionView):
    """Mark selected revisions as "under preparation"""
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        qs = self.get_queryset()
        document_ids = request.POST.getlist('document_ids')
        rev_ids = qs.filter(id__in=document_ids) \
            .values_list('latest_revision_id', flat=True)

        _class = self.category.revision_class()
        revisions = _class.objects.filter(id__in=rev_ids)
        revisions.update(under_preparation_by=self.request.user)

        index_revisions(revisions)
        return HttpResponseRedirect(self.get_redirect_url())


class BatchAckOfTransmittalReceipt(BaseDocumentBatchActionView):
    """Ack receipt of several transmittals at once."""
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_external:
            return HttpResponseForbidden(
                'Only contractors can acknowledge receipt of transmittals')

        document_ids = request.POST.getlist('document_ids')
        transmittals = self.get_queryset() \
            .filter(document_id__in=document_ids) \
            .filter(ack_of_receipt_date__isnull=True)
        revision_ids = list(
            transmittals.values_list('latest_revision_id', flat=True))

        # Update transmittal data
        transmittals.update(
            ack_of_receipt_date=timezone.now(),
            ack_of_receipt_author=self.request.user)

        # Update ES index
        _revision_class = self.category.revision_class()
        revisions = _revision_class.objects.filter(id__in=revision_ids)
        index_revisions(revisions)

        update_count = len(revision_ids)

        if update_count > 0:
            msg = _('You have successfully acknowledged receipt '
                    'of %s transmittals.') % update_count
        else:
            msg = _('We failed to acknowledge receipt of any transmittal.')

        notify(self.request.user, msg)

        return HttpResponseRedirect(self.get_redirect_url())


class CreateTransmittal(PermissionRequiredMixin, BaseDocumentBatchActionView):
    """Create a transmittal embedding the given documents"""
    permission_required = 'transmittals.add_outgoingtransmittal'
    http_method_names = ['post']

    def start_job(self, contenttype, document_ids):
        from_category_id = self.category.id
        to_category_id = self.request.POST.get('destination_category')
        recipients_ids = self.request.POST.getlist('recipients')
        contract_number = self.request.POST.get('contract_number')

        job = do_create_transmittal.delay(
            self.request.user.id,
            from_category_id,
            to_category_id,
            document_ids,
            contract_number,
            recipients_ids)
        return job


class AckOfTransmittalReceipt(LoginRequiredMixin,
                              DocumentListMixin,
                              DetailView):
    """Acknowledge receipt of a single transmittal."""
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_external:
            return HttpResponseForbidden(
                'Only contractors can acknowledge receipt of transmittals')

        transmittal = self.get_object()

        if transmittal.ack_of_receipt_date is not None:
            return HttpResponseForbidden(
                'Receipt already acknowledged')

        transmittal.ack_receipt(self.request.user, save=True)

        # Update ES index
        revisions = transmittal.get_all_revisions()
        index_revisions(revisions)

        return HttpResponseRedirect(transmittal.document.get_absolute_url())


class FileTransmittedDownload(LoginRequiredMixin, DetailView):
    """Allows a contractor to download a file_transmitted file."""

    def get_object(self):
        u"""Extract the correct revision."""

        if not self.request.user.is_external:
            raise Http404()

        # First, get the initial transmittal category
        organisation_slug = self.kwargs['organisation']
        category_slug = self.kwargs['category']
        category_qs = Category.objects \
            .select_related() \
            .filter(organisation__slug=organisation_slug) \
            .filter(category_template__slug=category_slug)
        category = get_object_or_404(category_qs)

        # Next, get the transmittal document
        document_key = self.kwargs['document_key']
        entities = get_entities(self.request.user)
        DocumentClass = category.document_class()
        document_qs = DocumentClass.objects \
            .select_related() \
            .filter(document__category=category) \
            .filter(document_key=document_key) \
            .filter(recipient_id__in=entities)
        document = get_object_or_404(document_qs)

        # Next, the related document
        related_key = self.kwargs['related_document_key']
        related_revision = self.kwargs['related_revision']
        revision_class = document.get_revisions_class()
        revision_qs = revision_class.objects \
            .select_related() \
            .filter(metadata__document__document_key=related_key) \
            .filter(transmittals=document) \
            .filter(revision=related_revision)
        linked_revision = get_object_or_404(revision_qs)
        return linked_revision

    def get(self, request, *args, **kwargs):
        u"""Serve the file."""

        rev = self.get_object()
        field_name = 'file_transmitted'
        return serve_model_file_field(rev, field_name)
