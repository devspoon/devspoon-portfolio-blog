from django.urls import path

from .views import GetInTouchView, PortfolioView

app_name = "portfolio"

urlpatterns = [
    path("", PortfolioView.as_view(), name="portfolio"),
    path("mail", GetInTouchView.as_view(), name="mail"),
]
