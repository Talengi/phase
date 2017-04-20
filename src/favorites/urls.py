from django.conf.urls import url

from .views import FavoriteList

urlpatterns = [

    # Favorites
    url(r'^$',
        FavoriteList.as_view(),
        name="favorite_list"),
]
