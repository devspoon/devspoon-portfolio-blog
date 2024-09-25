import logging

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db.models import Value
from django.http import Http404
from django.views.generic import TemplateView

from blog.models.blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost
from common.components.django_redis_cache_components import (
    dredis_cache_check_key,
    dredis_cache_get,
    dredis_cache_set,
)
from home.views.service.search import Search
from home.models import SiteInfo
from portfolio.models import AboutProjects

logger = logging.getLogger(getattr(settings, "HOME_LOGGER", "django"))

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class IndexView(TemplateView):
    template_name = "home/index.html"
    cache_prefix = "index"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        check_cached_key = dredis_cache_check_key(
            self.cache_prefix,
            0,
            "projects",
        )
        if check_cached_key:
            logger.debug(f"called redis cache - {self.__class__.__name__}")
            queryset = dredis_cache_get(self.cache_prefix, 0)
            context.update(queryset)
        else:
            context["projects"] = (
                AboutProjects.objects.all()
                .select_related("projectpost")
                .select_related("projectpost__author")
            )
            study = (
                OnlineStudyPost.activate_objects.get_data()[:3]
                .annotate(table=Value("OnlineStudy"))
                .values(
                    "pk",
                    "author",
                    "title",
                    "content",
                    "title_image",
                    "reply_count",
                    "visit_count",
                    "created_at",
                    "table",
                )
            )
            blog = (
                BlogPost.activate_objects.get_data()[:3]
                .annotate(table=Value("Blog"))
                .values(
                    "pk",
                    "author",
                    "title",
                    "content",
                    "title_image",
                    "reply_count",
                    "visit_count",
                    "created_at",
                    "table",
                )
            )
            opensource = (
                OpenSourcePost.activate_objects.get_data()[:3]
                .annotate(table=Value("OpenSource"))
                .values(
                    "pk",
                    "author",
                    "title",
                    "content",
                    "title_image",
                    "reply_count",
                    "visit_count",
                    "created_at",
                    "table",
                )
            )
            books = (
                BooksPost.activate_objects.get_data()[:3]
                .annotate(table=Value("Books"))
                .values(
                    "pk",
                    "author",
                    "title",
                    "content",
                    "title_image",
                    "reply_count",
                    "visit_count",
                    "created_at",
                    "table",
                )
            )
            latest = study.union(blog, all=False)
            latest = latest.union(opensource, all=False)
            context["latest"] = latest.union(books, all=False).order_by("created_at")[
                0:9
            ]
            caching_data = context.copy()
            [caching_data.pop(x, None) for x in ["view"]]
            logger.debug(f"called database - {self.__class__.__name__}")
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
        return context


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
