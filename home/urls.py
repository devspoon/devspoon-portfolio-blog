from django.urls import path

from .views.index import IndexView, SearchView, TermsOfServiceView, PrivacyPolicyView

app_name = "home"


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("search/queryset/", SearchView.as_view(), name="search_queryset"),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms-of-service", TermsOfServiceView.as_view(), name="terms_of_service"),
]
