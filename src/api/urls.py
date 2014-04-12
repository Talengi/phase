from django.conf.urls import patterns, url, include
from rest_framework import routers

from api import views


router = routers.DefaultRouter()
router.register('users', views.UserViewSet)


urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
