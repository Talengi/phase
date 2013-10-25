from django.conf.urls import patterns, url

from documents.views import (
    DefaultCategoryRedirect,
    DocumentList, DocumentFilter, DocumentCreate, DocumentDetail,
    DocumentEdit, DocumentDownload,
    FavoriteList, FavoriteCreate, FavoriteDelete,
    ProtectedDownload
)

urlpatterns = patterns(
    '',
    # Documents
    url(r'^$',
        DefaultCategoryRedirect.as_view(),
        name="document_list"),
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

    # Favorites
    url(r'^favorites/$',
        FavoriteList.as_view(),
        name="favorite_list"),
    url(r'^favorites/create/$',
        FavoriteCreate.as_view(),
        name="favorite_create"),
    url(r'^favorites/delete/(?P<pk>\d+)/$',
        FavoriteDelete.as_view(),
        name="favorite_delete"),

    # Downloads
    url(r'^download/$',
        DocumentDownload.as_view(),
        name="document_download"),
    url(r'^documents/(?P<file_name>.*)$',
        ProtectedDownload.as_view(),
        name="protected_download"),
)
