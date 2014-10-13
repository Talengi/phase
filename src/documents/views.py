import os
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

from django.utils import timezone
from django.conf import settings
from django.http import (
    HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
)
from django.core.servers.basehttp import FileWrapper
from django.views.generic import (
    View, ListView, DetailView, RedirectView)
from django.views.generic.edit import (
    ModelFormMixin, ProcessFormView, SingleObjectTemplateResponseMixin)
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.static import serve
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from rest_framework.renderers import JSONRenderer

from favorites.models import Favorite
from favorites.api.serializers import FavoriteSerializer
from categories.models import Category
from documents.models import Document
from documents.utils import compress_documents, save_document_forms
from documents.forms.models import documentform_factory
from documents.forms.utils import DocumentDownloadForm
from documents.forms.filters import filterform_factory
from notifications.models import notify
from accounts.views import LoginRequiredMixin, PermissionRequiredMixin


class DocumentListMixin(object):
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

    def get_context_data(self, **kwargs):
        context = super(DocumentListMixin, self).get_context_data(**kwargs)
        context.update({
            'organisation_slug': self.kwargs['organisation'],
            'category_slug': self.kwargs['category'],
            'category': self.category,
            'document_type': self.category.document_type(),
            'favorites': self.get_favorites()
        })
        return context

    def get_queryset(self):
        """Get queryset for listing documents.

        We get all Metadata depending on the category.

        """
        organisation_slug = self.kwargs['organisation']
        category_slug = self.kwargs['category']

        if not hasattr(self, 'category'):
            try:
                self.category = Category.objects \
                    .select_related(
                        'organisation',
                        'category_template__metadata_model') \
                    .get(
                        users=self.request.user,
                        organisation__slug=organisation_slug,
                        category_template__slug=category_slug)
            except Category.DoesNotExist:
                raise Http404('Category not found')

        DocumentClass = self.category.category_template.metadata_model.model_class()
        qs = DocumentClass.objects \
            .select_related(
                'latest_revision',
                'document',
                'document__category',
                'document__category__category_template',
                'document__category__organisation') \
            .filter(document__category=self.category)

        return qs

    def get_document_class(self):
        """Returns the document class hosted by this category."""
        qs = self.get_queryset()
        return qs.model

    def get_favorites(self):
        qs = Favorite.objects \
            .select_related('user') \
            .filter(user=self.request.user)
        serializer = FavoriteSerializer(qs, many=True)
        return JSONRenderer().render(serializer.data)


class BaseDocumentList(LoginRequiredMixin, DocumentListMixin, ListView):
    pass


class DocumentList(BaseDocumentList):
    template_name = 'documents/document_list.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentList, self).get_context_data(**kwargs)
        model = context['object_list'].model
        FilterForm = filterform_factory(model)

        qs = self.get_queryset()
        download_form = DocumentDownloadForm(queryset=qs)

        context.update({
            'download_form': download_form,
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


class DocumentFormMixin(DocumentListMixin):
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
            try:
                revision = self.object.get_revision(revision_number)
            except ObjectDoesNotExist:
                raise Http404(_('This revision does not exist'))
        else:
            revision = self.object.latest_revision

        return revision


class BaseDocumentFormView(DocumentFormMixin,
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


class DocumentDetail(LoginRequiredMixin, DocumentFormMixin, DetailView):
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
        form = DocumentForm(instance=document, read_only=True)

        revisions = document.get_all_revisions()
        RevisionForm = self.get_revisionform_class()
        for revision in revisions:
            revision.form = RevisionForm(instance=revision, read_only=True)

        context.update({
            'is_detail': True,
            'form': form,
            'revisions': revisions,
            'latest_revision': document.latest_revision,
        })
        return context


class DocumentCreate(PermissionRequiredMixin,
                     BaseDocumentFormView):
    permission_required = 'documents.add_document'
    context_object_name = 'document'
    template_name = 'documents/document_form.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        self.revision = None
        return super(DocumentCreate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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


class DocumentEdit(PermissionRequiredMixin,
                   BaseDocumentFormView):
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

        When we create a new revision, all the revision form
        fields must be empty.

        """
        document_form, revision_form = super(DocumentRevise, self).get_forms()

        # Let's take the complete field list, and build
        # a dict of empty strings from it.
        initial_data = dict(map(lambda x: (x, None), revision_form.fields.keys()))
        revision_form.initial = initial_data

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


class DocumentDownload(BaseDocumentList):

    def post(self, request, *args, **kwargs):
        # Deals with POST parameters
        qs = self.get_queryset()
        form = DocumentDownloadForm(self.request.POST, queryset=qs)
        if form.is_valid():
            data = form.cleaned_data
        else:
            raise Http404('Invalid parameters to download files.')

        # Generates the temporary zip file
        zip_filename = compress_documents(
            data['document_ids'],
            data['format'] or 'both',
            data['revisions'] or 'latest',
        )
        wrapper = FileWrapper(zip_filename)

        # Returns the zip file for download
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=download.zip'
        response['Content-Length'] = zip_filename.tell()
        zip_filename.seek(0)
        return response


class ProtectedDownload(LoginRequiredMixin, View):
    """Serve files with a web server after an ACL control.

    One might consider some alternate way, like this one:
    https://github.com/johnsensible/django-sendfile

    TODO Replace with django-downloadview

    """

    def get(self, request, *args, **kwargs):
        file_name = kwargs.get('file_name')

        # Prevent nasty things to happen
        clean_name = os.path.normpath(unquote(file_name))
        if clean_name.startswith('/') or '..' in clean_name:
            raise Http404('Nice try!')

        full_path = os.path.join(
            settings.REVISION_FILES_ROOT,
            clean_name)

        file_url = os.path.join(
            settings.REVISION_FILES_URL,
            clean_name)

        if not os.path.exists(full_path):
            raise Http404('File not found. Check the name.')

        # The X-sendfile Apache module makes it possible to serve file
        # directly from apache, but keeping a control from Django.
        # If we are in debug mode, and the module is unavailable, we fallback
        # to the django internal method to serve static files
        if settings.USE_X_SENDFILE:
            response = HttpResponse(mimetype='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name
            response['Content-Type'] = ''  # Apache will guess this
            response['X-Sendfile'] = full_path
            response['X-Accel-Redirect '] = file_url
            return response
        else:
            return serve(request, clean_name, settings.REVISION_FILES_ROOT)
