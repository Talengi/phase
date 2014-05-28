from django.conf.urls import patterns, url

from imports.views import ImportList, FileUpload, ImportStatus


urlpatterns = patterns(
    '',

    url(r'^$',
        ImportList.as_view(),
        name='import_list'),
    url(r'^import/$',
        FileUpload.as_view(),
        name='import_file'),
    url(r'^(?P<uid>[\w-]+)/$',
        ImportStatus.as_view(),
        name='import_status')
)
