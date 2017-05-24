from django.conf.urls import url

from categories.views import CategoryList


urlpatterns = [
    url(r'^$',
        CategoryList.as_view(),
        name="category_list"),
]
