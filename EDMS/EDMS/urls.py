from django.conf.urls import patterns, include, url
from django.http import HttpResponse
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^robots\.txt$', lambda r: HttpResponse(
        "User-agent: *\nDisallow: /",
        mimetype="text/plain")),
    url(r'^', include('documents.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
