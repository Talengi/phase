from django.conf.urls import patterns, url, include
from rest_framework import routers

from notifications.api import views as notifications_views
from favorites.api import views as favorites_views
from bookmarks.api import views as bookmarks_views


router = routers.DefaultRouter()
router.register(
    'notifications',
    notifications_views.NotificationViewSet,
    base_name='notification')
router.register(
    'favorites',
    favorites_views.FavoriteViewSet,
    base_name='favorite')
router.register(
    'bookmarks',
    bookmarks_views.BookmarkViewSet,
    base_name='bookmark')


urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
    url(r'^discussion/', include('discussion.api.urls')),
    url(r'accounts/', include('accounts.api.urls')),
)
