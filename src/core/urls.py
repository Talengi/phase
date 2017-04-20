from django.conf.urls import include, url
from django.http import HttpResponse
from django.contrib import admin
from django.conf import settings

from privatemedia.views import ProtectedDownload


admin.autodiscover()

admin.site.login_template = 'registration/login.html'

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('restapi.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^favorites/', include('favorites.urls')),
    url(r'^reviews/', include('reviews.urls')),
    url(r'^distriblists/', include('distriblists.urls')),
    url(r'^imports/', include('imports.urls')),
    url(r'^transmittals/', include('transmittals.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^exports/', include('exports.urls')),
    url(r'^feeds/', include('feeds.urls')),
    url(r'^protected/(?P<file_path>[-\w./]+)?$',
        ProtectedDownload.as_view(),
        name="protected_download"),
    url(r'^reporting/', include('reporting.urls')),
    url(r'^', include('categories.urls')),
    url(r'^', include('dashboards.urls')),
    url(r'^', include('documents.urls')),
    url(r'^robots\.txt$', lambda r: HttpResponse(
        "User-agent: *\nDisallow: /",
        content_type="text/plain")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
