from django import http
from django.views.generic import ListView
from django.utils import simplejson as json

from documents.models import Document
from documents.utils import filter_documents
from documents.forms import DocumentFilterForm


class JSONResponseMixin(object):
    """Source:
    https://docs.djangoproject.com/en/dev/topics/class-based-views/mixins/
    """
    def render_to_response(self, context):
        """Returns a JSON response containing 'context' as payload"""
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        """Construct an `HttpResponse` object."""
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        """Convert the `document_list` into a JSON object.

        Using DataTables conventions for fields' names.
        """
        documents = context['document_list']
        start = int(self.request.GET.get('iDisplayStart', 1))
        end = start + int(self.request.GET.get('iDisplayLength', 10))
        result = {
            "sEcho": self.request.GET.get("sEcho"),
            "iTotalRecords": Document.objects.all().count(),
            "iTotalDisplayRecords": len(documents),
            "aaData": [doc.jsonified() for doc in documents[start:end]]
        }
        return json.dumps(result)


class DocumentList(ListView):
    # We just need one document to set table's header
    queryset = Document.objects.all()[:1]


class DocumentFilter(JSONResponseMixin, ListView):
    model = Document

    def get_queryset(self):
        """Given DataTables' GET parameters, filter the initial queryset."""
        queryset = Document.objects.all()
        if self.request.method == "GET":
            form = DocumentFilterForm(self.request.GET)
            if form.is_valid():
                queryset = filter_documents(queryset, form.cleaned_data)

        return queryset
