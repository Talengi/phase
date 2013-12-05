from django.conf.urls import patterns, url

from documents.views import (
    DocumentList, DocumentFilter, DocumentCreate, DocumentDetail,
    DocumentEdit, DocumentDownload,
    ProtectedDownload
)

urlpatterns = patterns(
    '',

    # Filters
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/filter/$',
        DocumentFilter.as_view(),
        name="document_filter"),

    # Downloads
    url(r'^download/$',
        DocumentDownload.as_view(),
        name="document_download"),
    url(r'^files/(?P<file_name>[\w-]+)/$',
        ProtectedDownload.as_view(),
        name="protected_download"),

    # Documents
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        DocumentList.as_view(),
        name="category_document_list"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/create/$',
        DocumentCreate.as_view(),
        name="document_create"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?P<document_key>.+)/$',
        DocumentDetail.as_view(),
        name="document_detail"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?P<document_key>.+)/edit/$',
        DocumentEdit.as_view(),
        name="document_edit"),
)
