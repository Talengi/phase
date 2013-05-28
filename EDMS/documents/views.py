from datetime import datetime

from django import http
from django.http import HttpResponse, Http404
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (
    View, ListView, CreateView, DetailView, UpdateView, DeleteView
)
from django.utils import simplejson as json
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from documents.models import Document, DocumentRevision, Favorite
from documents.utils import filter_documents, compress_documents
from documents.forms import (
    DocumentFilterForm, DocumentForm, DocumentDownloadForm,
    DocumentRevisionForm, FavoriteForm
)
from documents.constants import (
    STATUSES, REVISIONS, UNITS, DISCIPLINES, DOCUMENT_TYPES, CLASSES
)


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

    def build_context(self, context):
        """
        Builds a dict from a context ready to be displayed as a table

        or JSON dumped.
        """
        documents = context['object_list']
        user = self.request.user
        if user.is_authenticated():
            favorites = Favorite.objects.filter(user=user)\
                                        .values_list('id', 'document')
            document2favorite = dict((v, k) for k, v in favorites)
        else:
            document2favorite = {}
        start = int(self.request.GET.get('start', 1))
        end = start + int(self.request.GET.get('length', 20))
        return {
            "total": Document.objects.all().count(),
            "display": len(documents),
            "data": [doc.jsonified(document2favorite)
                     for doc in documents[start:end]]
        }


class DocumentList(ListView, JSONResponseMixin):
    queryset = Document.objects.all()[:20]

    def get_context_data(self, **kwargs):
        user = self.request.user
        if user.is_authenticated():
            favorites = Favorite.objects.filter(user=user)\
                                        .values_list('id', 'document')
            document2favorite = dict((v, k) for k, v in favorites)
        else:
            document2favorite = {}

        context = super(DocumentList, self).get_context_data(**kwargs)
        context.update({
            'download_form': DocumentDownloadForm(),
            'form': DocumentFilterForm(),
            'documents_active': True,
            'document2favorite': document2favorite

        })
        context.update(self.build_context(context))
        return context


class DocumentDetail(DetailView):
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


class DocumentFilter(JSONResponseMixin, ListView):
    model = Document

    def get_queryset(self):
        """Given DataTables' GET parameters, filter the initial queryset."""
        queryset = Document.objects.all()
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


class DocumentCreate(DocumentRevisionMixin, CreateView):
    model = Document
    form_class = DocumentForm

    def get_context_data(self, **kwargs):
        context = super(DocumentCreate, self).get_context_data(**kwargs)
        context.update({
            'document_create': True,
        })
        return context


class DocumentEdit(DocumentRevisionMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    slug_url_kwarg = 'document_number'
    slug_field = 'document_number'

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


class DocumentDownload(View):

    def get(self, request, *args, **kwargs):
        # Deals with GET parameters
        form = DocumentDownloadForm(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data
        else:
            raise Http404('Invalid parameters to download files.')

        # Generates the temporary zip file
        zip_filename = compress_documents(
            data['document_numbers'],
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


class FavoriteList(ListView):
    model = Favorite
    template_name = 'documents/document_favorites.html'

    @method_decorator(login_required(login_url=reverse_lazy("document_list")))
    def dispatch(self, *args, **kwargs):
        return super(FavoriteList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FavoriteList, self).get_context_data(**kwargs)
        context.update({
            'favorites_active': True,
        })
        return context

    def get_queryset(self):
        """Filters favorites per authenticated user."""
        return self.model.objects.filter(user=self.request.user)


class FavoriteCreate(CreateView):
    model = Favorite
    form_class = FavoriteForm
    success_url = reverse_lazy('favorite_list')

    def form_valid(self, form):
        """
        If the form is valid, returns the id of the item created.
        """
        super(FavoriteCreate, self).form_valid(form)
        return HttpResponse(self.object.id)


class FavoriteDelete(DeleteView):
    model = Favorite
    success_url = reverse_lazy('document_list')
