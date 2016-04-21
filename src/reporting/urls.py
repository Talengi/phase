from django.conf.urls import patterns, url

from views import Report

urlpatterns = patterns(
    '',

    # Report home page
    url(r'^$',
        Report.as_view(),
        name='reports'),
)
