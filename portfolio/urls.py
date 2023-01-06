from django.urls import path, include
from .views import PortfolioView,WorkExperienceJsonView

app_name = "portfolio"

urlpatterns = [
    path('', PortfolioView.as_view(),name='portfolio'),
    path('json/',WorkExperienceJsonView.as_view(),name='work_experience'),
]