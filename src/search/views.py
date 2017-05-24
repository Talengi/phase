# -*- coding: utf-8 -*-



from braces.views import JSONResponseMixin

from search.builder import SearchBuilder
from documents.views import BaseDocumentList
from django.conf import settings


class SearchDocuments(JSONResponseMixin, BaseDocumentList):
    http_method_names = ['get']

    def get_queryset(self):
        """Given DataTables' GET parameters, filter the initial queryset."""
        super(SearchDocuments, self).get_queryset()
        if self.request.user.is_external:
            entities = self.get_external_filtering()
        else:
            entities = None
        try:
            builder = SearchBuilder(self.category,
                                    self.request.GET,
                                    filter_on_entities=entities)
            query = builder.build_query()
            query = builder.add_aggregations(query)
            results = query.execute()
        except RuntimeError:
            results = []

        return results

    def render_to_response(self, context, **response_kwargs):
        return self.render_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        response = self.get_queryset()
        start = int(self.request.GET.get('start', 0))
        end = start + int(self.request.GET.get('length', settings.PAGINATE_BY))
        total = response.hits.total
        display = min(end, total)
        search_data = [hit._d_ for hit in response.hits]
        aggregations = self.format_aggregations(response.aggregations)

        return {
            'total': total,
            'display': display,
            'data': search_data,
            'aggregations': aggregations,
        }

    def format_aggregations(self, aggregations):
        """Transfroms the ES "aggregations" response into something we can use.

        aggregations = {
            'filter_name': {
                'buckets': [
                    {'key': 'some_name', 'doc_count': 123},
                    …
                ]
            },
            …
        }

        We want :

        aggregations = {
            'filter_name': [{'some_name': 123}, …],
            …
        }

        """
        def flatten(bucket):
            key = bucket[0]
            buckets = bucket[1]['buckets']
            bucket_values = dict([(b['key'], b['doc_count']) for b in buckets])
            return (key, bucket_values)
        buckets = list(aggregations.to_dict().items())
        response = dict(list(map(flatten, buckets)))
        return response
