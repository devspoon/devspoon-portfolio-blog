from django.urls import path, include
from .views.index import IndexView

app_name = "home"

urlpatterns = [
    path('', IndexView.as_view(),name='index'),
]