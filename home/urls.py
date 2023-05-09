from django.urls import path

from common.error.error_views import (
    bad_request_page,
    page_not_found_page,
    server_error_page,
)

from .views.index import IndexView, SearchView

app_name = "home"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("search/queryset/", SearchView.as_view(), name="search_queryset"),
]
