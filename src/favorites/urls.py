from django.conf.urls import patterns, url

from .views import FavoriteList, FavoriteCreate, FavoriteDelete

urlpatterns = patterns(
    '',

    # Favorites
    url(r'^/$',
        FavoriteList.as_view(),
        name="favorite_list"),
    url(r'^create/$',
        FavoriteCreate.as_view(),
        name="favorite_create"),
    url(r'^delete/(?P<pk>\d+)/$',
        FavoriteDelete.as_view(),
        name="favorite_delete"),
)
