import logging

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from django.db.models import Count, Q
from django.db.models.functions import Lower, Trim
from django.views.generic import TemplateView, View

from blog.models.blog import Tag
from common.components.django_redis_cache_components import (
    cached,
    portfolio_key,
    work_experience_key,
)
from utils.email.async_send_email import send_mail_sync

from .forms import GetInTouchForm
from .models import (AboutProjects, EducationStudy, GetInTouchLog,
                     InterestedIn, PersonalInfo, Portfolio, WorkExperience)

logger = logging.getLogger(getattr(settings, "PORTFOLIO_LOGGER", "django"))


# Tech-stack diagram nodes (ADR-016), in diagram order; each node shows how many visible posts carry the tag.
STACK = ("django", "fastapi", "redis", "celery", "rabbitmq", "mysql")
_POST_RELATIONS = ("blogpost", "projectpost", "onlinestudypost", "opensourcepost", "bookspost")


def stack_counts():
    """{tag: visible post count} for STACK; tags match case- and space-insensitively."""
    rows = (
        Tag.objects.annotate(name=Lower(Trim("tag")))
        .filter(name__in=STACK)
        .values("name")
        .annotate(n=sum(
            Count(rel, distinct=True, filter=Q(**{f"{rel}__is_deleted": False, f"{rel}__is_hidden": False}))
            for rel in _POST_RELATIONS
        ))
    )
    counts = {row["name"]: row["n"] for row in rows}
    return {name: counts.get(name, 0) for name in STACK}


def get_language_index():
    return [
        i
        for i, v in enumerate(settings.LANGUAGES)
        if v[0] == translation.get_language()
    ]


# Create your views here.
class PortfolioView(TemplateView):
    template_name = "portfolio/portfolio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = get_language_index()
        # 언어별 키 1개. 무효화는 portfolio 모델 쓰기 뒤 common/cache_invalidation.py가 한다.
        context.update(cached(portfolio_key(lang[0]), lambda: self.build_context(lang)))
        # 폼은 요청마다 새로 만들어야 하므로 캐시에 넣지 않는다.
        context["get_in_touch_form"] = GetInTouchForm()
        return context

    @staticmethod
    def build_context(lang):
        portfolio = (
            Portfolio.objects.filter(language__in=lang)
            .prefetch_related("portfolio_summary")
            .first()
        )
        return {
            "info": PersonalInfo.objects.filter(language__in=lang).first(),
            "study": list(EducationStudy.objects.filter(language__in=lang)),
            "interested": list(InterestedIn.objects.filter(language__in=lang)),
            "projects": list(
                AboutProjects.objects.select_related("projectpost").select_related(
                    "projectpost__author"
                )
            ),
            "portfolio": portfolio,
            "stack": stack_counts(),
            # 서버에서 그리는 경력 타임라인(WorkExperienceJsonView와 같은 행)
            "experience": list(WorkExperience.objects.filter(language__in=lang)),
            "portfolio_summary": (
                list(portfolio.portfolio_summary.filter(language__in=lang))
                if portfolio is not None
                else []
            ),
        }


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
        lang = get_language_index()
        # 언어마다 다른 결과이므로 키에 언어를 넣는다(phase3 F-007).
        context = cached(
            work_experience_key(lang[0]),
            lambda: [
                self.make_context(data)
                for data in WorkExperience.objects.filter(language__in=lang)
            ],
        )
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
