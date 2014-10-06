from django.conf.urls import patterns, url, include
from rest_framework import routers

from accounts.api import views as accounts_views
from notifications.api import views as notifications_views
from favorites.api import views as favorites_views


router = routers.DefaultRouter()
router.register('users', accounts_views.UserViewSet)
router.register('notifications', notifications_views.MessageViewSet)
router.register('favorites', favorites_views.FavoriteViewSet)


urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
