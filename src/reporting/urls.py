from django.conf.urls import url

from views import Report

urlpatterns = [
    # Reports page
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/$',
        Report.as_view(),
        name='category_report'),
]
