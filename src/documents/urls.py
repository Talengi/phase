from django.conf.urls import patterns, url

from documents.views import (
    CategoryList,
    DocumentList, DocumentFilter, DocumentCreate, DocumentDetail,
    DocumentEdit, DocumentDownload,
    ProtectedDownload
)

urlpatterns = patterns(
    '',
    # Documents
    url(r'^$',
        CategoryList.as_view(),
        name="category_list"),
    url(r'^documents/(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        DocumentList.as_view(),
        name="category_document_list"),
    url(r'^detail/(?P<document_number>.*)/$',
        DocumentDetail.as_view(),
        name="document_detail"),
    url(r'^create/$',
        DocumentCreate.as_view(),
        name="document_create"),
    url(r'^edit/(?P<document_number>.*)/$',
        DocumentEdit.as_view(),
        name="document_edit"),

    # Filters
    url(r'^filter/(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        DocumentFilter.as_view(),
        name="document_filter"),

    # Downloads
    url(r'^download/$',
        DocumentDownload.as_view(),
        name="document_download"),
    url(r'^documents/(?P<file_name>.*)$',
        ProtectedDownload.as_view(),
        name="protected_download"),
)
