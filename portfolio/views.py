import logging

import re
import json
from django.contrib import messages
from django.conf import settings

#from django.core.mail import send_mail
from utils.email.async_send_email import send_mail
from django.template.loader import render_to_string

from django.utils import translation
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from .models import Portfolio, PersonalInfo, WorkExperience, EducationStudy, InterestedIn, AboutProjects, GetInTouchLog

logger = logging.getLogger(__name__)

# Create your views here.
class PortfolioView(TemplateView):
    template_name = 'portfolio/portfolio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # You can exchange model information using the code below.
        #print('get_current_language  : ',translation.get_language())

        context['info'] = PersonalInfo.objects.first()
        context['study'] = EducationStudy.objects.all()
        context['interested'] = InterestedIn.objects.all()
        context['projects'] = AboutProjects.objects.all().select_related('projectpost')
        portfolio = Portfolio.objects.prefetch_related('portfolio_summary').first()
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


class GetInTouchView(View):
    email_template_get_in_touch = '/email/get_in_touch.html'

    def post(self, request, *args, **kwargs):
        pattern = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        name = request.POST.get('name', '')
        emailfrom = request.POST.get('emailfrom', '')
        emailto = request.POST.get('emailto', '')
        number = request.POST.get('number', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')

        if not name :
            messages.error(self.request, "Name can't be empty.")
            return redirect(reverse('portfolio:portfolio'))

        if not emailfrom :
            messages.error(self.request, "email can't be empty.")
            return redirect(reverse('portfolio:portfolio'))

        if not pattern.match(emailfrom) :
            messages.error(self.request, "The email format is not correct.")
            return redirect(reverse('portfolio:portfolio'))

        if not subject :
            messages.error(self.request, "subject can't be empty.")
            return redirect(reverse('portfolio:portfolio'))

        if not message :
            messages.error(self.request, "message can't be empty.")
            return redirect(reverse('portfolio:portfolio'))

        email_context = {'name': name, 'emailfrom': emailfrom, 'number': number, 'message': message,}

        msg_html = render_to_string(settings.TEMPLATE_DIR + self.email_template_get_in_touch, email_context)

        send_mail(
            subject=subject,
            recipient_list= [emailto,],
            message=message,
            from_email=emailfrom,
            html_message=msg_html,
            fail_silently=True
        )

        GetInTouchLog.objects.create(name=name,state=True,email=emailfrom,phone_number=number,subject=subject,message=message)


        return redirect(reverse('portfolio:portfolio'))