import logging
import re

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View

from common.components.django_redis_cache_components import (
    dredis_cache_check_key,
    dredis_cache_get,
    dredis_cache_set,
)

# from django.core.mail import send_mail
from utils.email.async_send_email import send_mail

from .models import (
    AboutProjects,
    EducationStudy,
    GetInTouchLog,
    InterestedIn,
    PersonalInfo,
    Portfolio,
    WorkExperience,
)

logger = logging.getLogger(getattr(settings, "PORTFOLIO_LOGGER", "django"))

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


def get_language_index():
    return [
        i
        for i, v in enumerate(settings.LANGUAGES)
        if v[0] == translation.get_language()
    ]


# Create your views here.
class PortfolioView(TemplateView):
    template_name = "portfolio/portfolio.html"
    cache_prefix = "portfolio"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        check_cached_key = dredis_cache_check_key(
            self.cache_prefix,
            0,
            "info",
        )
        if check_cached_key:
            queryset = dredis_cache_get(self.cache_prefix, 0)
            context.update(queryset)
        else:
            lang = get_language_index()

            context["info"] = PersonalInfo.objects.filter(language__in=lang).first()
            context["study"] = EducationStudy.objects.filter(language__in=lang)
            context["interested"] = InterestedIn.objects.filter(language__in=lang)
            context["projects"] = AboutProjects.objects.select_related(
                "projectpost"
            ).select_related("projectpost__author")
            portfolio = (
                Portfolio.objects.filter(language__in=lang)
                .prefetch_related("portfolio_summary")
                .first()
            )
            context["portfolio"] = portfolio
            context["portfolio_summary"] = portfolio.portfolio_summary.filter(
                language__in=lang
            )
            caching_data = context.copy()

            [caching_data.pop(x, None) for x in ["view"]]
            dredis_cache_set(
                self.cache_prefix,
                0,
                **caching_data,
            )
        logger.debug(f"final context : {context}")
        return context


class WorkExperienceJsonView(View):
    cache_prefix = "portfolio"

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
                "color": data.get_color_display(),
                "created_at": data.created_at.strftime("%Y-%m-%d"),
            }
        else:
            return {
                "pk": data.pk,
                "start_year": data.project_start_date.strftime("%Y"),
                "project_start_date": data.project_start_date.strftime("%Y/%m/%d"),
                "project_end_date": data.project_end_date.strftime("%Y/%m/%d"),
                "title": data.title,
                "role": data.role,
                "summary": data.summary,
                "content": data.content,
                "color": data.get_color_display(),
                "created_at": data.created_at.strftime("%Y-%m-%d"),
            }

    def get(self, request, *args, **kwargs):
        check_cached_key = dredis_cache_check_key(
            self.cache_prefix,
            0,
            "WorkExperience",
        )
        if check_cached_key:
            context = dredis_cache_get(self.cache_prefix, 0, "WorkExperience")
        else:
            lang = get_language_index()
            data = WorkExperience.objects.filter(language__in=lang)
            context = list(map(self.make_context, data))
            caching_data = {}
            caching_data["WorkExperience"] = context
            dredis_cache_set(
                self.cache_prefix,
                0,
                **caching_data,
            )
        logger.debug(f"final context : {context}")
        return JsonResponse(context, safe=False)


class GetInTouchView(View):
    email_template_get_in_touch = "/email/get_in_touch.html"

    def post(self, request, *args, **kwargs):
        pattern = re.compile("^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        name = request.POST.get("name", "")
        emailfrom = request.POST.get("emailfrom", "")
        emailto = request.POST.get("emailto", "")
        number = request.POST.get("number", "")
        subject = request.POST.get("subject", "")
        message = request.POST.get("message", "")

        if not name:
            messages.error(self.request, "Name can't be empty.")
            return redirect(reverse("portfolio:portfolio"))

        if not emailfrom:
            messages.error(self.request, "email can't be empty.")
            return redirect(reverse("portfolio:portfolio"))

        if not pattern.match(emailfrom):
            messages.error(self.request, "The email format is not correct.")
            return redirect(reverse("portfolio:portfolio"))

        if not subject:
            messages.error(self.request, "subject can't be empty.")
            return redirect(reverse("portfolio:portfolio"))

        if not message:
            messages.error(self.request, "message can't be empty.")
            return redirect(reverse("portfolio:portfolio"))

        email_context = {
            "name": name,
            "emailfrom": emailfrom,
            "number": number,
            "message": message,
        }

        msg_html = render_to_string(
            settings.TEMPLATE_DIR + self.email_template_get_in_touch, email_context
        )

        send_mail(
            subject=subject,
            recipient_list=[
                emailto,
            ],
            message=message,
            from_email=emailfrom,
            html_message=msg_html,
            fail_silently=True,
        )

        GetInTouchLog.objects.create(
            name=name,
            state=True,
            email=emailfrom,
            phone_number=number,
            subject=subject,
            message=message,
        )

        return redirect(reverse("portfolio:portfolio"))
