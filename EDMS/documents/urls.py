from django.conf.urls import patterns, url

from documents.views import (
    DocumentList, DocumentFilter, DocumentCreate, DocumentDetail,
    DocumentEdit, DocumentDownload,
    FavoriteList, FavoriteCreate, FavoriteDelete,
)

urlpatterns = patterns(
    '',
    url(r'^filter/$',
        DocumentFilter.as_view(),
        name="document_filter"),
    url(r'^create/$',
        DocumentCreate.as_view(),
        name="document_create"),
    url(r'^detail/(?P<document_number>.*)/$',
        DocumentDetail.as_view(),
        name="document_detail"),
    url(r'^edit/(?P<document_number>.*)/$',
        DocumentEdit.as_view(),
        name="document_edit"),
    url(r'^download/$',
        DocumentDownload.as_view(),
        name="document_download"),
    url(r'^favorites/delete/(?P<pk>\d+)/$',
        FavoriteDelete.as_view(),
        name="favorite_delete"),
    url(r'^favorites/create/$',
        FavoriteCreate.as_view(),
        name="favorite_create"),
    url(r'^favorites/$',
        FavoriteList.as_view(),
        name="favorite_list"),
    url(r'^$',
        DocumentList.as_view(),
        name="document_list"),
)
