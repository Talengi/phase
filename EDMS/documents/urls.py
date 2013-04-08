from django.conf.urls import patterns, url

from documents.views import DocumentList

urlpatterns = patterns(
    '',
    url(r'^$', DocumentList.as_view(), name="document_list"),
)
