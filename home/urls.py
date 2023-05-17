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
    path("400", bad_request_page, name="400"),
    path("404", page_not_found_page, name="404"),
    path("500", server_error_page, name="500"),
]
