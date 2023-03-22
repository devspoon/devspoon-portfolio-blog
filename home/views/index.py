import logging

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.utils import make_template_fragment_key
from django.db.models import Value
from django.http import Http404
from django.views.generic import TemplateView, View

from blog.models.blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost
from home.views.service.search import Search
from portfolio.models import AboutProjects

logger = logging.getLogger(getattr(settings, "HOME_LOGGER", "django"))

# Create your views here.

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class IndexView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "index" in cache:
            context["latest"] = cache.get("home:index")
        else:
            context["projects"] = (
                AboutProjects.objects.all()
                .select_related("projectpost")
                .select_related("projectpost__author")
            )
            study = (
                OnlineStudyPost.objects.all()[:3]
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
                BlogPost.objects.all()[:3]
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
                OpenSourcePost.objects.all()[:3]
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
                BooksPost.objects.all()[:3]
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
                :9
            ]
            cache.set("home:index", context["latest"], timeout=CACHE_TTL)
        return context


class PrivacyPolicyView(TemplateView):
    template_name = "pages/privacy-policy.html"


class TermsOfServiceView(TemplateView):
    template_name = "pages/terms-of-service.html"


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
