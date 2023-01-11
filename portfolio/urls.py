from django.urls import path, include
from .views import PortfolioView, WorkExperienceJsonView, GetInTouchView

app_name = "portfolio"

urlpatterns = [
    path('', PortfolioView.as_view(),name='portfolio'),
    path('json/',WorkExperienceJsonView.as_view(),name='work_experience'),
    path('mail', GetInTouchView.as_view(),name='mail'),
]