from django.conf.urls import patterns, include, url
from django.http import HttpResponse
from django.contrib import admin
admin.autodiscover()

admin.site.login_template = 'registration/login.html'

urlpatterns = patterns(
    '',
    url(r'^', include('documents.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^robots\.txt$', lambda r: HttpResponse(
        "User-agent: *\nDisallow: /",
        mimetype="text/plain")),
    url(r'^admin/', include(admin.site.urls)),
)
