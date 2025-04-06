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
from validate_email import validate_email
from validate_email.exceptions import AddressFormatError, Error

from common.components.django_redis_cache_components import (
    dredis_cache_check_key, dredis_cache_delete, dredis_cache_get,
    dredis_cache_set)
# from django.core.mail import send_mail
from utils.email.async_send_email import send_mail

from .models import (AboutProjects, EducationStudy, GetInTouchLog,
                     InterestedIn, PersonalInfo, Portfolio, WorkExperience)

      # 일반적인 이메일 유효성 오류의 기본 클래스                   # MX 레코드 없음 오류



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
        lang = get_language_index()
        check_cached_key = dredis_cache_check_key(
            self.cache_prefix + ":" + str(lang[0]),
            0,
            "info",
        )
        if check_cached_key:
            logger.debug(f"called redis cache - {self.__class__.__name__}")
            queryset = dredis_cache_get(
                self.cache_prefix + ":" + str(lang[0]),
                0,
            )
            context.update(queryset)
        else:
            logger.debug(f"called database - {self.__class__.__name__}")
            dredis_cache_delete(
                self.cache_prefix,
            )
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

            if portfolio is not None:
                context["portfolio_summary"] = portfolio.portfolio_summary.filter(
                    language__in=lang
                )
            else:
                context["portfolio_summary"] = []  # 또는 None으로 설정

            caching_data = context.copy()

            [caching_data.pop(x, None) for x in ["view"]]
            if caching_data:
                logger.debug(
                    f"redis cache - {self.__class__.__name__} caching_data exists"
                )
                dredis_cache_set(
                    self.cache_prefix + ":" + str(lang[0]),
                    0,
                    **caching_data,
                )
            else:
                logger.debug(
                    f"redis cache - {self.__class__.__name__} caching_data not exists"
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
            logger.debug("called redis cache - WorkExperienceJsonView")
            context = dredis_cache_get(self.cache_prefix, 0, "WorkExperience")
        else:
            logger.debug("called database - WorkExperienceJsonView")
            lang = get_language_index()
            data = WorkExperience.objects.filter(language__in=lang)
            context = list(map(self.make_context, data))
            caching_data = {}
            caching_data["WorkExperience"] = context
            if caching_data:
                logger.debug(
                    f"redis cache - {self.__class__.__name__} caching_data exists"
                )
                dredis_cache_set(
                    self.cache_prefix,
                    0,
                    **caching_data,
                )
            else:
                logger.debug(
                    f"redis cache - {self.__class__.__name__} caching_data not exists"
                )
        logger.debug(f"final context : {context}")
        return JsonResponse(context, safe=False)


class GetInTouchView(View):
    email_template_get_in_touch = "/email/get_in_touch.html"

    def check_email_validation_with_dns(self, email: str) -> [str, bool]:
        try:
            if email is None:
                return "", False
            logger.debug(
                "GetInTouchView.check_email_validation_with_dns email :",
                extra={"email": email},
            )

            _, domain = email.rsplit("@", 1)

            if "test" in domain.lower():
                raise AddressFormatError("Incorrect domain. Please enter the domain you actually use.")

            is_valid = validate_email(
                email_address=email,
                check_format=True,          # 이메일 형식 검증
                check_blacklist=True,       # 블랙리스트 도메인 검증
                check_dns=True,             # DNS MX 레코드 검증
                dns_timeout=10,             # DNS 타임아웃 10초
                check_smtp=False,            # SMTP 연결 통한 실제 이메일 존재 여부 검증
                smtp_timeout=10,            # SMTP 타임아웃 10초
                smtp_helo_host=settings.SMTP_HOST,  # SMTP HELO 호스트명
                smtp_from_address=settings.SMTP_FROM_ADDRESS,  # SMTP FROM 주소
                smtp_skip_tls=False,        # TLS 사용
                smtp_debug=False            # 디버그 출력 비활성화
            )
            if not is_valid:
                raise Error("The email failed validation. Please enter the email address you actually use")

            logger.debug(
                "GetInTouchView email validated"
            )

            return is_valid

        except (Error,  ValueError) as e:
            logger.debug(
                "Error :",
                extra={"GetInTouchView.error : ": str(e)},
            )
            return is_valid

    def post(self, request, *args, **kwargs):
        pattern = re.compile("^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        name = request.POST.get("name", "")
        emailfrom = request.POST.get("emailfrom", "")
        emailto = request.POST.get("emailto", "")
        number = request.POST.get("number", "")
        subject = request.POST.get("subject", "")
        message = request.POST.get("message", "")

        rt = self.check_email_validation_with_dns(emailfrom)

        if not rt:
            logger.debug(
                "The email failed validation. Please enter the email address you actually use",
                extra={"email : ": emailto},
            )
            messages.error(request, "The email failed validation. Please enter the email address you actually use")
            return redirect(reverse("portfolio:portfolio"))

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
        subject_email = subject + " - " + emailfrom

        send_mail(
            subject=subject_email,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            html_message=msg_html,
            fail_silently=False,
        )

        GetInTouchLog.objects.create(
            name=name,
            state=True,
            email=emailfrom,
            phone_number=number,
            subject=subject,
            message=message,
        )
        messages.success(request, "Your email has been successfully delivered.")
        return redirect(reverse("portfolio:portfolio"))

        GetInTouchLog.objects.create(
            name=name,
            state=True,
            email=emailfrom,
            phone_number=number,
            subject=subject,
            message=message,
        )
        messages.success(request, "Your email has been successfully delivered.")
        return redirect(reverse("portfolio:portfolio"))
        return redirect(reverse("portfolio:portfolio"))

        GetInTouchLog.objects.create(
            name=name,
            state=True,
            email=emailfrom,
            phone_number=number,
            subject=subject,
            message=message,
        )
        messages.success(request, "Your email has been successfully delivered.")
        return redirect(reverse("portfolio:portfolio"))
        return redirect(reverse("portfolio:portfolio"))

        GetInTouchLog.objects.create(
            name=name,
            state=True,
            email=emailfrom,
            phone_number=number,
            subject=subject,
            message=message,
        )
        messages.success(request, "Your email has been successfully delivered.")
        return redirect(reverse("portfolio:portfolio"))
        GetInTouchLog.objects.create(
            name=name,
            state=True,
            email=emailfrom,
            phone_number=number,
            subject=subject,
            message=message,
        )
        messages.success(request, "Your email has been successfully delivered.")
        return redirect(reverse("portfolio:portfolio"))
        return redirect(reverse("portfolio:portfolio"))
        GetInTouchLog.objects.create(
            name=name,
            state=True,
            email=emailfrom,
            phone_number=number,
            subject=subject,
            message=message,
        )
        messages.success(request, "Your email has been successfully delivered.")
        return redirect(reverse("portfolio:portfolio"))
