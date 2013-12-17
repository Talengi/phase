import os
import json
from datetime import datetime
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, Http404
from django.core.servers.basehttp import FileWrapper
from django.views.generic import (
    View, ListView, CreateView, DetailView, UpdateView, RedirectView)
from django.core.urlresolvers import reverse
from django.views.static import serve
from django.shortcuts import get_object_or_404
from braces.views import JSONResponseMixin

from favorites.models import Favorite
from categories.models import Category
from documents.models import Document
from documents.utils import filter_documents, compress_documents
from documents.forms.models import documentform_factory
from documents.forms.utils import DocumentDownloadForm
from documents.forms.filters import filterform_factory

from accounts.views import LoginRequiredMixin, PermissionRequiredMixin


class DocumentListMixin(object):
    """Base class for listing documents.

    This is the base class to factorize code fetching documents
    of the correct type.

    """
    def get_context_data(self, **kwargs):
        context = super(DocumentListMixin, self).get_context_data(**kwargs)
        context.update({
            'organisation_slug': self.kwargs['organisation'],
            'category_slug': self.kwargs['category'],
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
                    .select_related('category_template__metadata_model') \
                    .get(users=self.request.user,
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

    def get_serializable_document_list(self, context, total=None):
        """Returns document list data in a json serializable format.

        TODO The conceptual purity of this API is not really satisfying.
        Let's rewrite it some day.

        """
        start = int(self.request.GET.get('start', 0))
        end = start + int(self.request.GET.get('length', settings.PAGINATE_BY))
        documents = context['object_list']
        total = total if total else documents.count()
        display = min(end, total)

        user = self.request.user
        favorites = Favorite.objects \
            .filter(user=user) \
            .values_list('id', 'document')
        document2favorite = dict((v, k) for k, v in favorites)

        data = self.get_cached_data(documents, document2favorite, start, end)

        return {
            'total': total,
            'display': display,
            'data': data,
        }

    def get_cached_data(self, documents, document2favorite, start, end):
        """Get existing cached data, or set it otherwise."""
        CACHE_DATA_KEY = '{document2favorite}_{get_parameters}'.format(
            # We want to update the cache if favorites have changed
            document2favorite=document2favorite,
            # ...and if filtering GET parameters have changed
            get_parameters=self.request.get_full_path(),
        ).replace(' ', '_')[:249]  # memcached restrictions
        data = cache.get(CACHE_DATA_KEY)
        if data is None:
            data = [doc.jsonified(document2favorite)
                    for doc in documents[start:end]]
            cache.set(CACHE_DATA_KEY, data, settings.CACHE_TIMEOUT_SECONDS)

        return data


class BaseDocumentList(LoginRequiredMixin, DocumentListMixin, ListView):
    pass


class DocumentList(BaseDocumentList):
    template_name = 'documents/document_list.html'
    paginate_by = settings.PAGINATE_BY

    def get_context_data(self, **kwargs):
        context = super(DocumentList, self).get_context_data(**kwargs)
        json_data = self.get_serializable_document_list(context,
                                                        context['paginator'].count)
        model = context['object_list'].model
        FilterForm = filterform_factory(model)

        context.update({
            'download_form': DocumentDownloadForm(),
            'form': FilterForm(),
            'documents_active': True,
            'initial_data': json.dumps(json_data),
            'items_per_page': self.paginate_by,
            'document_class': self.get_document_class(),
        })
        return context


class DocumentFilter(JSONResponseMixin, BaseDocumentList):

    def render_to_response(self, context, **response_kwargs):
        return self.render_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        full_context = super(DocumentFilter, self).get_context_data(**kwargs)
        context = self.get_serializable_document_list(full_context)
        return context

    def get_queryset(self):
        """Given DataTables' GET parameters, filter the initial queryset."""
        queryset = super(DocumentFilter, self).get_queryset()
        if self.request.method == "GET":
            FilterForm = filterform_factory(queryset.model)
            form = FilterForm(self.request.GET)
            if form.is_valid():
                queryset = filter_documents(queryset, form.cleaned_data)
            else:
                raise Exception(form.errors)
        return queryset


class DocumentRedirect(RedirectView):
    """Redirects from short document url to full url."""

    permanent = False  # document location can change

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
    def get_form_class(self):
        return documentform_factory(self.get_document_class())

    def get_revisionform_class(self):
        document = self.object
        return documentform_factory(document.get_revision_class())


class DocumentDetail(LoginRequiredMixin, DocumentFormMixin, DetailView):
    slug_url_kwarg = 'document_key'
    slug_field = 'document_key'
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
            .update(last_view_date=datetime.now())

        return response

    def get_context_data(self, **kwargs):
        context = super(DocumentDetail, self).get_context_data(**kwargs)
        document = context['document']

        DocumentForm = self.get_form_class()
        form = DocumentForm(instance=document, read_only=True)

        revisions = document.get_all_revisions()
        RevisionForm = self.get_revisionform_class()
        for revision in revisions:
            revision.form = RevisionForm(instance=revision)
        context.update({
            'is_detail': True,
            'form': form,
            'revisions': revisions,
        })
        return context


class DocumentRevisionMixin(object):
    """
    Deal with revisions' auto-creation on model creation/edition.
    """
    #def form_valid(self, form):
    #    self.object = form.save()
    #    # Deal with the new revision if any
    #    data = form.cleaned_data
    #    current_revision = data['current_revision']
    #    if not DocumentRevision.objects.filter(
    #        revision=current_revision,
    #        document=self.object
    #    ).exists():
    #        DocumentRevision.objects.create(
    #            document=self.object,
    #            revision=current_revision,
    #            revision_date=data['current_revision_date'],
    #            native_file=data['native_file'],
    #            pdf_file=data['pdf_file'],
    #        )
    #    return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """Redirect to a different URL given the button clicked by the user."""
        if "save-create" in self.request.POST:
            url = reverse('document_create')
        else:
            url = self.object.get_absolute_url()
        return url


class DocumentCreate(PermissionRequiredMixin, LoginRequiredMixin, DocumentFormMixin, DocumentRevisionMixin, CreateView):
    model = Document
    permission_required = 'documents.add_document'

    def get_context_data(self, **kwargs):
        context = super(DocumentCreate, self).get_context_data(**kwargs)
        context.update({
            'document_create': True,
        })
        return context

    def get_success_url(self):
        """Redirect to a different URL given the button clicked by the user."""
        if "save-create" in self.request.POST:
            url = reverse('document_create')
        else:
            url = reverse('category_list')
        return url


class DocumentEdit(PermissionRequiredMixin, DocumentFormMixin, DocumentRevisionMixin, UpdateView):
    model = Document
    slug_url_kwarg = 'document_key'
    slug_field = 'document_key'
    permission_required = 'documents.change_document'
    template_name = 'documents/document_form.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        context = super(DocumentEdit, self).get_context_data(**kwargs)
        # Add a context var to make the difference with creation view
        context.update({
            'is_edit': True,
        })
        return context

    def get_success_url(self):
        """Redirect to a different URL given the button clicked by the user."""
        if "save-view" in self.request.POST:
            url = self.object.get_absolute_url()
        else:
            url = reverse('category_list')
        return url


class DocumentDownload(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        # Deals with GET parameters
        form = DocumentDownloadForm(self.request.GET)
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
            return response
        else:
            return serve(request, clean_name, settings.REVISION_FILES_ROOT)
