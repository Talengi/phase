from django.conf.urls import patterns, url

from documents.views import DocumentList, DocumentFilter

urlpatterns = patterns(
    '',
    url(r'^filter/$',
        DocumentFilter.as_view(),
        name="document_filter"),
    url(r'^$',
        DocumentList.as_view(),
        name="document_list"),
)
