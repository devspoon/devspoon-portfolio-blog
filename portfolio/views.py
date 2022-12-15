from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import Http404

# Create your views here.
class PortfolioView(TemplateView):
    template_name = 'portfolio/portfolio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
