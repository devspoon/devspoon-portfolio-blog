import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from django.views.generic import TemplateView, View

from common.components.django_redis_cache_components import (
    dredis_cache_check_key, dredis_cache_delete, dredis_cache_get,
    dredis_cache_set)
from utils.email.async_send_email import send_mail_sync

from .forms import GetInTouchForm
from .models import (AboutProjects, EducationStudy, GetInTouchLog,
                     InterestedIn, PersonalInfo, Portfolio, WorkExperience)

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

        # 캐시 저장이 끝난 뒤에 넣는다. 폼은 요청마다 새로 만들어야 하고
        # 캐시에 들어가면 모든 방문자가 같은 인스턴스를 보게 된다.
        context["get_in_touch_form"] = GetInTouchForm()

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

    def post(self, request, *args, **kwargs):
        form = GetInTouchForm(request.POST)

        if not form.is_valid():
            for error in form.errors.values():
                messages.error(request, error[0])
            logger.debug(
                "GetInTouchView invalid submission",
                extra={"errors": form.errors.get_json_data(escape_html=True)},
            )
            return redirect(reverse("portfolio:portfolio"))

        data = form.cleaned_data

        # 문의는 메일 발송 결과와 무관하게 먼저 접수한다.
        # 메일 벤더 장애로 문의 자체가 유실되면 안 된다.
        log = GetInTouchLog.objects.create(
            name=data["name"],
            state=True,
            status=GetInTouchLog.MailStatus.RECEIVED,
            email=data["emailfrom"],
            phone_number=data["number"],
            subject=data["subject"],
            message=data["message"],
        )

        # 수신자는 hidden input(emailto)이 아니라 서버 설정값으로 고정한다.
        delivered = self.send_notification(data)

        log.status = (
            GetInTouchLog.MailStatus.SENT
            if delivered
            else GetInTouchLog.MailStatus.FAILED
        )
        log.save(update_fields=["status"])

        if delivered:
            messages.success(request, "Your email has been successfully delivered.")
        else:
            # 접수는 성공했으므로 실패로 안내하지 않는다.
            messages.warning(
                request,
                "Your message has been received, but the notification email is "
                "delayed. We will get back to you.",
            )

        return redirect(reverse("portfolio:portfolio"))

    def send_notification(self, data: dict) -> bool:
        email_context = {
            "name": data["name"],
            "emailfrom": data["emailfrom"],
            "number": data["number"],
            "message": data["message"],
        }

        msg_html = render_to_string(
            settings.TEMPLATE_DIR + self.email_template_get_in_touch, email_context
        )

        return send_mail_sync(
            subject=f"{data['subject']} - {data['emailfrom']}",
            message=data["message"],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            html_message=msg_html,
            fail_silently=False,
        )
