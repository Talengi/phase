from django.conf.urls import patterns, url

from categories.views import CategoryList


urlpatterns = patterns(
    '',
    url(r'^$',
        CategoryList.as_view(),
        name="category_list"),
)
