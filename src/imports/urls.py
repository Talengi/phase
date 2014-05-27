from django.conf.urls import patterns, url

from imports.views import FileUpload, ImportStatus


urlpatterns = patterns(
    '',

    url(r'^$',
        FileUpload.as_view(),
        name='import_file'),
    url(r'^(?P<uid>[\w-]+)/$',
        ImportStatus.as_view(),
        name='import_status')
)
