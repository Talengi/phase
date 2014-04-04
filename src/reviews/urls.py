from django.conf.urls import patterns, url

from reviews.views import (
    DocumentList
)

urlpatterns = patterns(
    '',

    # Documents
    url(r'^$',
        DocumentList.as_view(),
        name="review_document_list"),
)
