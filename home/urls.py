from django.urls import path

from .views.index import IndexView, SearchView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import Indexitemap

app_name = "home"


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("search/queryset/", SearchView.as_view(), name="search_queryset"),
]
