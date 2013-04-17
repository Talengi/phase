from django.conf.urls import patterns, url

from documents.views import (
    DocumentList, DocumentFilter, DocumentCreate, DocumentDetail,
    DocumentEdit
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
    url(r'^$',
        DocumentList.as_view(),
        name="document_list"),
)
