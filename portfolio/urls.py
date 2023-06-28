from django.urls import path

from .views import GetInTouchView, PortfolioView, WorkExperienceJsonView

from django.contrib.sitemaps.views import sitemap
from .sitemaps import Portfolioitemap

app_name = "portfolio"

sitemaps = {
    "portfolio": Portfolioitemap,
}

urlpatterns = [
    path("", PortfolioView.as_view(), name="portfolio"),
    path("json/", WorkExperienceJsonView.as_view(), name="work_experience"),
    path("mail", GetInTouchView.as_view(), name="mail"),
]
