from django.conf.urls import patterns, url


from search.views import SearchDocuments


urlpatterns = patterns(
    '',

    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        SearchDocuments.as_view(),
        name='search_documents'),
)
