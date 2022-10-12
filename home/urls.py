from django.urls import path, include
from .views.index import IndexView, SearchView

app_name = "home"

urlpatterns = [
    path('', IndexView.as_view(),name='index'),
    path('search/queryset/', SearchView.as_view(),name='search_queryset'),
]