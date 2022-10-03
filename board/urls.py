from django.urls import path, include
from .views.visit_board import VisiterListView

app_name = "board"

urlpatterns = [
    path('visiter/', VisiterListView.as_view(), name='visit'),
]