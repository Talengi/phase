# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.utils import timezone
from django.conf import settings
from django.http import (
    HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
)
from django.core.servers.basehttp import FileWrapper
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    ListView, DetailView, RedirectView, DeleteView)
from django.views.generic.edit import (
    ModelFormMixin, ProcessFormView, SingleObjectTemplateResponseMixin)
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from rest_framework.renderers import JSONRenderer

from accounts.models import get_entities
from favorites.models import Favorite
from favorites.api.serializers import FavoriteSerializer
from bookmarks.models import get_user_bookmarks
from bookmarks.api.serializers import BookmarkSerializer
from categories.views import CategoryMixin
from documents.models import Document
from documents.utils import save_document_forms
from documents.forms.models import documentform_factory
from documents.forms.filters import filterform_factory
from notifications.models import notify
from privatemedia.views import serve_model_file_field


class DocumentListMixin(CategoryMixin):
    """Base class for listing documents.

    This is the base class to factorize code fetching documents
    of the correct type.

    """
    slug_url_kwarg = 'document_key'
    slug_field = 'document_key'

    def breadcrumb_section(self):
        return None

    def breadcrumb_subsection(self):
        return self.category

    def get_external_filtering(self):
        """This is used to filter Outgoing transmittals for
        third party users"""
        return get_entities(self.request.user)

    def get_context_data(self, **kwargs):
        self.get_external_filtering()
        context = super(DocumentListMixin, self).get_context_data(**kwargs)
        context.update({
            'organisation_slug': self.kwargs['organisation'],
            'category_slug': self.kwargs['category'],
            'category': self.category,
            'document_type': self.category.document_type(),
            'favorites': self.get_favorites(),
            'bookmarks': self.get_bookmarks(self.request.user, self.category),
        })
        return context

    def get_queryset(self):
        """Get queryset for listing documents.

        We get all Metadata depending on the category.

        """
        DocumentClass = self.category.document_class()
        qs = DocumentClass.objects \
            .select_related() \
            .filter(document__category=self.category)

        entities = self.get_external_filtering()
        if self.request.user.is_external and entities:
            # todo: check qs has recipient_id
            qs = qs.filter(recipient_id__in=entities)
        return qs

    def get_document_class(self):
        """Returns the document class hosted by this category."""
        return self.category.document_class()

    def get_favorites(self):
        qs = Favorite.objects \
            .select_related('user') \
            .filter(user=self.request.user)
        serializer = FavoriteSerializer(qs, many=True)
        return JSONRenderer().render(serializer.data)

    def get_bookmarks(self, user, category):
        bookmarks = get_user_bookmarks(user, category)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return JSONRenderer().render(serializer.data)


class BaseDocumentList(LoginRequiredMixin, DocumentListMixin, ListView):
    pass


class BaseDocumentBatchActionView(PermissionRequiredMixin, BaseDocumentList):
    """Performs a task on several documents at once.

    This operation can be quite time consuming when many documents are reviewed
    at once, and this is expected to be normal by the users. We display a nice
    progress bar while the user waits.

    Since the user is already waiting, we also perform elasticsearch indexing
    synchronously, so at the end of the operation, the document list displayed
    is in sync.

    """
    permission_required = 'documents.can_control_document'

    def get_redirect_url(self, *args, **kwargs):
        """Redirects to document list after that."""
        return reverse('category_document_list', args=[
            self.kwargs.get('organisation'),
            self.kwargs.get('category')])

    def post(self, request, *args, **kwargs):
        document_ids = request.POST.getlist('document_ids')
        document_class = self.get_document_class()
        contenttype = ContentType.objects.get_for_model(document_class)

        job = self.start_job(contenttype, document_ids)

        poll_url = reverse('task_poll', args=[job.id])
        data = {'poll_url': poll_url}
        return HttpResponse(json.dumps(data), content_type='application/json')

    def start_job(self, content_type, document_ids):
        raise NotImplementedError()


class DocumentList(BaseDocumentList):
    template_name = 'documents/document_list.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentList, self).get_context_data(**kwargs)
        model = context['object_list'].model
        FilterForm = filterform_factory(model)

        context.update({
            'form': FilterForm(),
            'documents_active': True,
            'paginate_by': settings.PAGINATE_BY,
            'sort_by': model._meta.ordering[0],
            'document_class': self.get_document_class(),
        })
        return context


class DocumentRedirect(RedirectView):
    """Redirects from short document url to full url."""

    # Permanent redirections are cached and doc location can change, so...
    permanent = False

    def get_redirect_url(self, **kwargs):
        key = kwargs.get('document_key')
        qs = Document.objects.select_related(
            'category__organisation',
            'category__category_template')
        document = get_object_or_404(qs, document_key=key)
        return reverse('document_detail', args=[
            document.category.organisation.slug,
            document.category.slug,
            document.document_key])


class DocumentFormMixin(object):
    def breadcrumb_object(self):
        return self.object

    def get_form_class(self):
        """Get the document form edition form class."""
        return documentform_factory(self.get_document_class())

    def get_revisionform_class(self):
        """Get the correct revision form edition form class."""
        document = self.object

        # If there is no document (e.g when creating a new document)
        # we need to create a dummy object just to get the associated
        # revision class. TODO find a better way to do this
        if not document:
            document = self.get_document_class()()

        return documentform_factory(document.get_revision_class())

    def get_forms(self):
        """Returns both the document and revision forms."""
        kwargs = self.get_form_kwargs()

        document_form_class = self.get_form_class()
        document_form = document_form_class(**kwargs)

        kwargs.update({'instance': self.revision})
        revision_form_class = self.get_revisionform_class()
        revision_form = revision_form_class(**kwargs)

        return document_form, revision_form

    def get_revision(self):
        """Get the edited revision."""
        revision_number = self.kwargs.get('revision', None)
        if revision_number:
            revision = self.object.get_revision(revision_number)
            if revision is None:
                raise Http404(_('This revision does not exist'))
        else:
            revision = self.object.latest_revision

        return revision


class BaseDocumentFormView(LoginRequiredMixin,
                           PermissionRequiredMixin,
                           DocumentListMixin,
                           DocumentFormMixin,
                           SingleObjectTemplateResponseMixin,
                           ModelFormMixin,
                           ProcessFormView):
    """Base view class to display a document form."""

    def get(self, request, *args, **kwargs):
        document_form, revision_form = self.get_forms()
        return self.render_to_response(self.get_context_data(
            document_form=document_form,
            revision_form=revision_form
        ))

    def post(self, request, *args, **kwargs):
        document_form, revision_form = self.get_forms()
        if document_form.is_valid() and revision_form.is_valid():
            return self.form_valid(document_form, revision_form)
        else:
            return self.form_invalid(document_form, revision_form)

    def get_form_kwargs(self):
        kwargs = super(BaseDocumentFormView, self).get_form_kwargs()

        # If category is not set, the "get_queryset" method was not called
        # TODO clean this
        if not hasattr(self, 'category'):
            _qs = self.get_queryset()  # noqa

        kwargs.update({'category': self.category})
        return kwargs

    def form_valid(self, document_form, revision_form):
        """Saves both the document and it's revision."""
        document, self.object, self.revision = save_document_forms(
            document_form, revision_form, self.category
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, document_form, revision_form):
        """Render the form with errors."""
        return self.render_to_response(self.get_context_data(
            document_form=document_form,
            revision_form=revision_form
        ))


class DocumentDetail(LoginRequiredMixin,
                     DocumentListMixin,
                     DocumentFormMixin,
                     DetailView):
    context_object_name = 'document'
    template_name = 'documents/document_detail.html'

    def get(self, request, *args, **kwargs):
        """Update the favorite's timestamp for the current user if any."""
        response = super(DocumentDetail, self).get(request, *args, **kwargs)

        # Upgrade last time the favorite was last seen
        # If not favorited, the query does nothing and it's ok
        Favorite.objects \
            .filter(document=self.object.document) \
            .filter(user=self.request.user) \
            .update(last_view_date=timezone.now())

        return response

    def get_context_data(self, **kwargs):
        context = super(DocumentDetail, self).get_context_data(**kwargs)
        document = self.object

        DocumentForm = self.get_form_class()
        form = DocumentForm(
            instance=document,
            category=self.category,
            read_only=True)

        revisions = document.get_all_revisions()
        RevisionForm = self.get_revisionform_class()
        latest_revision = None
        for revision in revisions:
            revision.form = RevisionForm(
                instance=revision,
                request=self.request,
                category=self.category,
                read_only=True)
            # Get latest revision without additional query
            if latest_revision is None or latest_revision.revision < revision.revision:
                latest_revision = revision

        context.update({
            'is_detail': True,
            'form': form,
            'revisions': revisions,
            'latest_revision': latest_revision,
        })
        context.update(latest_revision.detail_view_context(self.request))
        return context


class DocumentCreate(BaseDocumentFormView):
    permission_required = 'documents.add_document'
    context_object_name = 'document'
    template_name = 'documents/document_form.html'

    def check_if_creation_is_available(self):
        if not self.category.use_creation_form:
            raise PermissionDenied(
                'Document creation is disabled for this category')

    def get(self, request, *args, **kwargs):
        self.check_if_creation_is_available()
        self.object = None
        self.revision = None
        return super(DocumentCreate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.check_if_creation_is_available()
        self.object = None
        self.revision = None
        return super(DocumentCreate, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DocumentCreate, self).get_context_data(**kwargs)
        context.update({
            'document_create': True,
        })
        return context

    @transaction.atomic
    def form_valid(self, document_form, revision_form):
        """Saves both the document and it's revision."""
        doc, metadata, revision = save_document_forms(
            document_form, revision_form, self.category)

        message_text = '''You created the document
                       <a href="%(url)s">%(key)s (%(title)s)</a>'''
        message_data = {
            'url': doc.get_absolute_url(),
            'key': doc.document_key,
            'title': doc.title
        }
        notify(self.request.user, _(message_text) % message_data)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """Redirect to a different URL given the button clicked by the user."""
        if "save-create" in self.request.POST:
            url = reverse('document_create', args=[
                self.kwargs['organisation'],
                self.kwargs['category']
            ])
        else:
            url = reverse('category_document_list', args=[
                self.kwargs['organisation'],
                self.kwargs['category']
            ])
        return url


class DocumentEdit(BaseDocumentFormView):
    """Edit a document and a selected revision."""
    permission_required = 'documents.change_document'
    context_object_name = 'document'
    template_name = 'documents/document_form.html'

    # We don't subclass UpdateView because there is too much to rewrite
    # since we manage two forms at a time.

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.revision = self.get_revision()
        return super(DocumentEdit, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.revision = self.get_revision()
        return super(DocumentEdit, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DocumentEdit, self).get_context_data(**kwargs)
        # Add a context var to make the difference with creation view
        context.update({
            'is_edit': True,
            'revision': self.revision,
        })
        return context

    def get_success_url(self):
        """Redirect to a different URL given the button clicked by the user."""
        if "save-view" in self.request.POST:
            url = self.object.get_absolute_url()
        else:
            url = reverse('category_document_list', args=[
                self.kwargs['organisation'],
                self.kwargs['category'],
            ])
        return url


class DocumentDelete(LoginRequiredMixin,
                     PermissionRequiredMixin,
                     DocumentListMixin,
                     DeleteView):
    """Edit a document and a selected revision."""
    permission_required = 'documents.can_control_document'
    raise_exception = True
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        """Delete the document and associated data.

        We need to delete the top level document object. Thus, metadata and
        revisions will also be deleted.

        """
        document = self.object.document
        success_url = self.get_success_url()
        document.delete()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.latest_revision.is_under_review():
            return HttpResponseForbidden('Documents under review cannot be deleted')
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.category.get_absolute_url()


class DocumentRevisionDelete(DocumentDelete):
    """Delete only the latest document revision."""

    def delete(self, request, *args, **kwargs):
        all_revisions = list(self.object.get_all_revisions())

        if len(all_revisions) < 2:
            return HttpResponseForbidden('Cannot delete a single latest revision')

        latest_revision = all_revisions[0]
        previous_revision = all_revisions[1]

        self.object.latest_revision = previous_revision
        self.object.save()

        latest_revision.delete()

        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return self.object.get_absolute_url()


class DocumentRevise(DocumentEdit):
    """Creates a new revision for the document."""

    def get(self, *args, **kwargs):
        doc = self.get_object()
        revision = doc.latest_revision
        if revision.is_under_review():
            return HttpResponseForbidden('You cannot revise a document during review')

        return super(DocumentRevise, self).get(*args, **kwargs)

    def get_revision(self):
        """returns an empty revision, since we are creating a new one."""
        return None

    def get_forms(self):
        """Returns both the document and revision forms.

        We went the revision fields to be blank, so we need to get rid of
        default values.

        We also want to keep the previous' revision distribution list.

        """
        document_form, revision_form = super(DocumentRevise, self).get_forms()

        latest_revision = self.object.latest_revision
        initial = latest_revision.get_new_revision_initial(revision_form)
        revision_form.initial = initial

        return document_form, revision_form

    @transaction.atomic
    def form_valid(self, document_form, revision_form):
        """Saves both the document and it's revision."""
        document, self.object, self.revision = save_document_forms(
            document_form, revision_form, self.category)

        message_text = '''You created revision %(rev)s for document
                       <a href="%(url)s">%(key)s (%(title)s)</a>'''
        message_data = {
            'rev': self.revision.name,
            'url': self.object.get_absolute_url(),
            'key': self.object.document_key,
            'title': self.object.title
        }
        notify(self.request.user, _(message_text) % message_data)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """Add a context var to make the difference with creation view"""
        next_revision = self.object.document.current_revision + 1
        context = super(DocumentRevise, self).get_context_data(**kwargs)
        context.update({
            'is_revise': True,
            'next_revision': '{:02d}'.format(next_revision)
        })
        return context


class DocumentDownload(BaseDocumentList):

    def post(self, request, *args, **kwargs):
        _class = self.category.document_class()
        form_data = self.request.POST
        qs = Document.objects.filter(category=self.category)
        form = _class.get_document_download_form(form_data, queryset=qs)
        if form.is_valid():
            data = form.cleaned_data
        else:
            raise Http404('Invalid parameters to download files.')

        # Generates the temporary zip file
        zip_filename = _class.compress_documents(data['document_ids'], **data)
        zip_filename.seek(0)
        wrapper = FileWrapper(zip_filename)

        # Returns the zip file for download
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=download.zip'
        response['Content-Length'] = zip_filename.tell()
        zip_filename.seek(0)
        return response


class DocumentFileDownload(LoginRequiredMixin,
                           CategoryMixin,
                           DetailView):
    """Download files from a MetadataRevision FileField."""
    http_method_names = ['get']

    def get_object(self, queryset=None):
        """Get a single MetadataRevision FileField instance."""
        key = self.kwargs.get('document_key')
        revision = self.kwargs.get('revision')

        qs = self.category.revision_class().objects \
            .filter(document__document_key=key) \
            .filter(document__category=self.category) \
            .filter(revision=revision)
        revision = get_object_or_404(qs)
        return revision

    def get(self, request, *args, **kwargs):
        revision = self.get_object()
        field_name = self.kwargs.get('field_name')
        return serve_model_file_field(revision, field_name)
