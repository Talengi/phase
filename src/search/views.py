from elasticsearch_dsl import Search, Q
from braces.views import JSONResponseMixin

from search import elastic
from documents.views import BaseDocumentList
from documents.forms.filters import filterform_factory
from django.conf import settings


class SearchDocuments(JSONResponseMixin, BaseDocumentList):
    http_method_names = ['get']

    def render_to_response(self, context, **response_kwargs):
        return self.render_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        response = self.get_queryset()
        start = int(self.request.GET.get('start', 0))
        end = start + int(self.request.GET.get('length', settings.PAGINATE_BY))
        total = response.hits.total
        display = min(end, total)
        search_data = [hit._d_ for hit in response.hits]
        return {
            'total': total,
            'display': display,
            'data': search_data
        }

    def get_queryset(self):
        """Given DataTables' GET parameters, filter the initial queryset."""
        queryset = super(SearchDocuments, self).get_queryset()
        FilterForm = filterform_factory(queryset.model)
        form = FilterForm(self.request.GET)
        if form.is_valid():
            s = self.build_search_query(
                queryset.model,
                self.category.document_type(),
                form.cleaned_data)
            response = s.execute()
            return response

        return []

    def build_search_query(self, Model, document_type, data):
        """Builds an elasticsearch query."""

        s = Search(using=elastic, doc_type=document_type) \
            .index(settings.ELASTIC_INDEX)

        # Filter fields
        filter_fields = Model.PhaseConfig.filter_fields
        for field in filter_fields:
            value = data.get(field, None)
            if value:
                s = s.filter(Q({'term': {field: value}}))

        # Search query
        search_terms = data.get('search_terms', None)
        if search_terms:
            searchable_fields = Model.PhaseConfig.searchable_fields
            s = s.query('multi_match', query=search_terms, fields=searchable_fields)

        # Sort query
        order = data.get('sort_by', 'sort_key') or 'sort_key'
        s = s.sort(order)

        # Pagination
        s = s.extra(
            from_=data.get('start', 0),
            size=data.get('size', settings.PAGINATE_BY)
        )

        return s
