import os
from datetime import datetime

from django import http
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, Http404
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (
    View, ListView, CreateView, DetailView, UpdateView, DeleteView,
    RedirectView
)
from django.utils import simplejson as json
from django.core.urlresolvers import reverse
from django.views.static import serve
from django.shortcuts import get_object_or_404
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

from documents.models import Document, DocumentRevision, Favorite
from documents.utils import filter_documents, compress_documents
from documents.forms import (
    DocumentFilterForm, DocumentForm, DocumentDownloadForm,
    DocumentRevisionForm, FavoriteForm
)

from accounts.models import Category
from accounts.views import LoginRequiredMixin, PermissionRequiredMixin


class JSONResponseMixin(object):
    """Source:
    https://docs.djangoproject.com/en/dev/topics/class-based-views/mixins/
    """
    def render_to_response(self, context):
        """Returns a JSON response containing 'context' as payload"""
        return self.get_json_response(json.dumps(self.build_context(context)))

    def get_json_response(self, content, **httpresponse_kwargs):
        """Construct an `HttpResponse` object."""
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def build_context(self, context, total=None):
        """
        Builds a dict from a context ready to be displayed as a table

        or JSON dumped.
        """
        documents = context['object_list']
        user = self.request.user
        start = int(self.request.GET.get('start', 0))
        end = start + int(self.request.GET.get('length', settings.PAGINATE_BY))
        if total is None:
            total = documents.count()
        display = min(end, total)
        if user.is_authenticated():
            favorites = Favorite.objects.filter(user=user)\
                                        .values_list('id', 'document')
            document2favorite = dict((v, k) for k, v in favorites)
        else:
            document2favorite = {}
        data = [doc.jsonified(document2favorite)
                for doc in documents[start:end]]
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
        return {
            "total": total,
            "display": display,
            "data": data,
        }


class DocumentListMixin(object):
    def get_queryset(self):
        organisation = self.kwargs['organisation']
        category = self.kwargs['category']

        qs = Document.objects \
            .filter(categories__users=self.request.user) \
            .filter(categories__organisation__slug=organisation) \
            .filter(categories__category_template__slug=category)

        return qs


class CategoryList(LoginRequiredMixin, ListView):
    """Display a list of user categories"""

    def get_queryset(self, **kwargs):
        qs = Category.objects \
            .filter(users=self.request.user) \
            .select_related('category_template', 'organisation') \
            .order_by('organisation__name')

        return qs


class DocumentList(LoginRequiredMixin, DocumentListMixin,
                   ListView, JSONResponseMixin):
    paginate_by = settings.PAGINATE_BY

    def get_context_data(self, **kwargs):
        context = super(DocumentList, self).get_context_data(**kwargs)
        initial_data = self.build_context(context,
                                          context["paginator"].count)
        context.update({
            'download_form': DocumentDownloadForm(),
            'form': DocumentFilterForm(),
            'documents_active': True,
            'initial_data': json.dumps(initial_data),
            'items_per_page': settings.PAGINATE_BY,
            'organisation_slug': self.kwargs['organisation'],
            'category_slug': self.kwargs['category']
        })
        return context


class DocumentDetail(LoginRequiredMixin, DetailView):
    model = Document
    slug_url_kwarg = 'document_number'
    slug_field = 'document_number'

    def get_object(self):
        """Update the favorite's timestamp for the current user if any."""
        document = super(DocumentDetail, self).get_object()
        if self.request.user.is_authenticated():
            try:
                favorite = Favorite.objects.get(
                    document=document,
                    user=self.request.user
                )
            except Favorite.DoesNotExist:
                favorite = None
            if favorite:
                favorite.last_view_date = datetime.now()
                favorite.save()
        return document

    def get_context_data(self, **kwargs):
        context = super(DocumentDetail, self).get_context_data(**kwargs)
        document = context['document']
        # Attach a form for each revision linked to the current document
        revisions = document.documentrevision_set.all()
        for revision in revisions:
            revision.form = DocumentRevisionForm(instance=revision)
        # Add the form to the context to be rendered in a disabled way
        context.update({
            'is_detail': True,
            'form': DocumentForm(instance=document),
            'revisions': revisions,
        })
        return context


class DocumentFilter(LoginRequiredMixin, DocumentListMixin,
                     JSONResponseMixin, ListView):
    model = Document

    def get_queryset(self):
        """Given DataTables' GET parameters, filter the initial queryset."""
        queryset = super(DocumentFilter, self).get_queryset()
        if self.request.method == "GET":
            form = DocumentFilterForm(self.request.GET)
            if form.is_valid():
                queryset = filter_documents(queryset, form.cleaned_data)
            else:
                raise Exception(form.errors)
        return queryset


class DocumentRevisionMixin(object):
    """
    Deal with revisions' auto-creation on model creation/edition.
    """
    def form_valid(self, form):
        self.object = form.save()
        # Deal with the new revision if any
        data = form.cleaned_data
        current_revision = data['current_revision']
        if not DocumentRevision.objects.filter(
            revision=current_revision,
            document=self.object
        ).exists():
            DocumentRevision.objects.create(
                document=self.object,
                revision=current_revision,
                revision_date=data['current_revision_date'],
                native_file=data['native_file'],
                pdf_file=data['pdf_file'],
            )
        return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """Redirect to a different URL given the button clicked by the user."""
        if "save-create" in self.request.POST:
            url = reverse('document_create')
        else:
            url = self.object.get_absolute_url()
        return url


class DocumentCreate(PermissionRequiredMixin, LoginRequiredMixin, DocumentRevisionMixin, CreateView):
    model = Document
    form_class = DocumentForm
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
            url = reverse('document_list')
        return url


class DocumentEdit(PermissionRequiredMixin, DocumentRevisionMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    slug_url_kwarg = 'document_number'
    slug_field = 'document_number'
    permission_required = 'documents.change_document'

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
            url = reverse('document_list')
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


class FavoriteList(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'documents/document_favorites.html'

    def get_context_data(self, **kwargs):
        context = super(FavoriteList, self).get_context_data(**kwargs)
        context.update({
            'favorites_active': True,
        })
        return context

    def get_queryset(self):
        """Filters favorites per authenticated user."""
        return self.model.objects.filter(user=self.request.user)


class FavoriteCreate(LoginRequiredMixin, CreateView):
    model = Favorite
    form_class = FavoriteForm
    success_url = reverse_lazy('favorite_list')

    def form_valid(self, form):
        """
        If the form is valid, returns the id of the item created.
        """
        super(FavoriteCreate, self).form_valid(form)
        return HttpResponse(self.object.id)


class FavoriteDelete(LoginRequiredMixin, DeleteView):
    model = Favorite
    success_url = reverse_lazy('document_list')
