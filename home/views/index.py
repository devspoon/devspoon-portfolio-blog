import logging

from django.conf import settings
from django.db.models import Value
from django.http import Http404
from django.views.generic import TemplateView

from blog.models.blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost
from common.components.django_redis_cache_components import INDEX_KEY, cached
from home.views.service.search import Search
from home.models import SiteInfo
from portfolio.models import AboutProjects

logger = logging.getLogger(getattr(settings, "HOME_LOGGER", "django"))


class IndexView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 키 1개(v2:index). 무효화는 글·프로젝트 쓰기 뒤 common/cache_invalidation.py가 한다.
        context.update(cached(INDEX_KEY, self.build_context))
        return context

    @staticmethod
    def build_context():
        def latest_of(model, table):
            return (
                model.activate_objects.get_data()[:3]
                .annotate(table=Value(table))
                .values(
                    "pk",
                    "title",
                    "content",
                    "title_image",
                    "reply_count",
                    "visit_count",
                    "created_at",
                    "table",
                )
            )

        # 게시판마다 3개씩 읽어 Python에서 합친다. 조각 쿼리의 union은 SQLite가 지원하지 않는다(phase3 F-011).
        # 게시판 이름(table)이 달라 union의 중복 제거와 결과가 같다.
        rows = [
            row
            for model, table in [
                (OnlineStudyPost, "OnlineStudy"),
                (BlogPost, "Blog"),
                (OpenSourcePost, "OpenSource"),
                (BooksPost, "Books"),
            ]
            for row in latest_of(model, table)
        ]
        # 최신 글부터(template-phase3 STOP 2 결정)
        latest = sorted(rows, key=lambda row: row["created_at"], reverse=True)[:9]
        projects = (
            AboutProjects.objects.all()
            .select_related("projectpost")
            .select_related("projectpost__author")
        )
        # QuerySet이 아니라 평가된 list를 저장한다.
        return {"projects": list(projects), "latest": list(latest)}


class SearchView(TemplateView, Search):
    template_name = "base/search_result_board_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        page_number = self.request.GET.get("page", "1")
        keyword = self.request.GET.get("keyword")
        tag = self.request.GET.get("tag")

        if not tag and not keyword:
            raise Http404("Keyword or tag is essentials")

        if tag:
            return self.queryset_tag_search(tag, page_number, self.paginate_by)

        if keyword:
            return self.queryset_keyword_search(keyword, page_number, self.paginate_by)


class PrivacyPolicyView(TemplateView):
    template_name = "pages/privacy-policy.html"

    def get_context_data(self, **kwargs):
        context = SiteInfo.objects.values("privacy_policy").first()
        return context


class TermsOfServiceView(TemplateView):
    template_name = "pages/terms-of-service.html"

    def get_context_data(self, **kwargs):
        context = SiteInfo.objects.values("terms_of_service").first()
        return context
