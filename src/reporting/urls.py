from django.conf.urls import patterns, url

from views import Report

urlpatterns = patterns(
    '',
    # Reports page
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        Report.as_view(),
        name='category_report'),
)
