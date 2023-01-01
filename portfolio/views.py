import logging

from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import Http404
from .models import Portfolio, PersonalInfo, PortfolioSummary, WorkExperience, EducationStudy, InterestedIn, AboutProjects

logger = logging.getLogger(__name__)

# Create your views here.
class PortfolioView(TemplateView):
    template_name = 'portfolio/portfolio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['info'] = PersonalInfo.objects.all()
        #context['work'] = WorkExperience.objects.all()
        context['study'] = EducationStudy.objects.all()
        context['interested'] = InterestedIn.objects.all()
        context['projects'] = AboutProjects.objects.all().select_related('projectpost')
        portfolio = Portfolio.objects.prefetch_related('portfolio_summary').get(pk=1)
        context['portfolio'] = portfolio
        context['portfolio_summary'] = portfolio.portfolio_summary.all()
        return context
