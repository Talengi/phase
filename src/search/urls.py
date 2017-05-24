from django.conf.urls import url


from search.views import SearchDocuments


urlpatterns = [
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        SearchDocuments.as_view(),
        name='search_documents'),
]
