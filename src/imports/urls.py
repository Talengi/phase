from django.conf.urls import patterns, url

from imports.views import FileUpload


urlpatterns = patterns(
    '',

    url(r'^$',
        FileUpload.as_view(),
        name='import')
)
