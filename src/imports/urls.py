from django.conf.urls import url

from imports.views import ImportList, FileUpload, ImportStatus, ImportTemplate


urlpatterns = [

    url(r'^$',
        ImportList.as_view(),
        name='import_list'),
    url(r'^template/$',
        ImportTemplate.as_view(),
        name='import_template'),
    url(r'^import/$',
        FileUpload.as_view(),
        name='import_file'),
    url(r'^(?P<uid>[\w-]+)/$',
        ImportStatus.as_view(),
        name='import_status')
]
