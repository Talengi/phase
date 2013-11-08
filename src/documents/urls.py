from django.conf.urls import patterns, url

from documents.views import (
    CategoryList,
    DocumentList, DocumentFilter, DocumentCreate, DocumentDetail,
    DocumentEdit, DocumentDownload,
    ProtectedDownload
)

urlpatterns = patterns(
    '',

    # Filters
    url(r'^/(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/filter/$',
        DocumentFilter.as_view(),
        name="document_filter"),

    # Downloads
    url(r'^download/$',
        DocumentDownload.as_view(),
        name="document_download"),
    url(r'^documents/(?P<file_name>.*)$',
        ProtectedDownload.as_view(),
        name="protected_download"),

    # Documents
    url(r'^$',
        CategoryList.as_view(),
        name="category_list"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        DocumentList.as_view(),
        name="category_document_list"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/create/$',
        DocumentCreate.as_view(),
        name="document_create"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?<document_number>.*)/$',
        DocumentDetail.as_view(),
        name="document_detail"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?<document_number>.*)/edit/$',
        DocumentEdit.as_view(),
        name="document_edit"),
)
