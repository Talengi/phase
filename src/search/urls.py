from django.conf.urls import patterns, url


from search.views import SearchDocuments, ExportDocuments


urlpatterns = patterns(
    '',

    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        SearchDocuments.as_view(),
        name='search_documents'),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+).csv$',
        ExportDocuments.as_view(),
        name='export_documents'),
)
