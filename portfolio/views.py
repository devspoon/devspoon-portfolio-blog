import logging

import json
from django.http import JsonResponse
from django.core import serializers
from django.shortcuts import render, redirect
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
        context['study'] = EducationStudy.objects.all()
        context['interested'] = InterestedIn.objects.all()
        context['projects'] = AboutProjects.objects.all().select_related('projectpost')
        portfolio = Portfolio.objects.prefetch_related('portfolio_summary').get(pk=1)
        context['portfolio'] = portfolio
        context['portfolio_summary'] = portfolio.portfolio_summary.all()
        return context


class WorkExperienceJsonView(View):

    def make_context(self, data):
        if not data.project_end_date:
            return {
            "pk": data.pk,
            "start_year": data.project_start_date.strftime("%Y"),
            "project_start_date": data.project_start_date.strftime("%Y/%m/%d"),
            "title": data.title,
            "role": data.role,
            "summary": data.summary,
            "content": data.content,
            "color":data.get_color_display(),
            "created_at": data.created_at.strftime("%Y-%m-%d"),
        }
        else :
            return {
            "pk": data.pk,
            "start_year": data.project_start_date.strftime("%Y"),
            "project_start_date": data.project_start_date.strftime("%Y/%m/%d"),
            "project_end_date": data.project_end_date.strftime("%Y/%m/%d"),
            "title": data.title,
            "role": data.role,
            "summary": data.summary,
            "content": data.content,
            "color":data.get_color_display(),
            "created_at": data.created_at.strftime("%Y-%m-%d"),
        }


    def get(self, request, *args, **kwargs):
        data = WorkExperience.objects.all()
        context = list(
            map(self.make_context, data)
        )

        return JsonResponse(context, safe=False)