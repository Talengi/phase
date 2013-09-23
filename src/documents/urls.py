from django.conf.urls import patterns, url

from documents.views import (
    DocumentList, DocumentFilter, DocumentCreate, DocumentDetail,
    DocumentEdit, DocumentDownload,
    FavoriteList, FavoriteCreate, FavoriteDelete,
)

urlpatterns = patterns(
    '',
    # Documents
    url(r'^$',
        DocumentList.as_view(),
        name="document_list"),
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
    url(r'^filter/$',
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

    # Other
    url(r'^download/$',
        DocumentDownload.as_view(),
        name="document_download"),
)
