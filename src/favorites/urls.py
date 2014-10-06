from django.conf.urls import patterns, url

from .views import FavoriteList

urlpatterns = patterns(
    '',

    # Favorites
    url(r'^$',
        FavoriteList.as_view(),
        name="favorite_list"),
)
