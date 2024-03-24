"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from blog.admin.common_admin import blog_admin_site
from board.admin.common_admin import board_admin_site
from home.admin.default_admin import home_admin_site
from portfolio.admin import portfolio_admin_site
from users.admin import user_admin_site
from django.views.generic import TemplateView

from django.contrib.sitemaps.views import sitemap, index

from portfolio.sitemaps import PortfolioSitemap
from home.sitemaps import IndexSitemap
from board.sitemaps import (
    NoticeListSitemap,
    NoticeSitemap,
    VisiterListSitemap,
    VisiterSitemap,
    ReactivationListSitemap,
    ReactivationSitemap,
)
from blog.sitemaps import (
    ProjectPostListSitemap,
    ProjectPostSitemap,
    OnlineStudyPostListSitemap,
    OnlineStudyPostSitemap,
    BlogPostListSitemap,
    BlogPostSitemap,
    OpenSourcePostListSitemap,
    OpenSourcePostSitemap,
    BooksPostListSitemap,
    BooksPostSitemap,
)

from django.contrib import admin

from django.conf.urls import handler400, handler403, handler404, handler500

sitemaps = {
    "portfolio": PortfolioSitemap,
    "index": IndexSitemap,
    "notice_list": NoticeListSitemap,
    "notice_detail": NoticeSitemap,
    "visiter_list": VisiterListSitemap,
    "visiter_detail": VisiterSitemap,
    "reactivation_list": ReactivationListSitemap,
    "reactivation_detail": ReactivationSitemap,
    "project_list": ProjectPostListSitemap,
    "project_detail": ProjectPostSitemap,
    "online_study_list": OnlineStudyPostListSitemap,
    "online_study_detail": OnlineStudyPostSitemap,
    "blog_list": BlogPostListSitemap,
    "blog_detail": BlogPostSitemap,
    "opensource_list": OpenSourcePostListSitemap,
    "opensource_detail": OpenSourcePostSitemap,
    "books_list": BooksPostListSitemap,
    "books_detail": BooksPostSitemap,
}

error_patterns = []

admin_patterns = [
    path("default/", admin.site.urls),
    path("home/", home_admin_site.urls),
    path("users/", user_admin_site.urls),
    path("blog/", blog_admin_site.urls),
    path("board/", board_admin_site.urls),
    path("portfolio/", portfolio_admin_site.urls),
]

urlpatterns = [
    path("admin/", include(admin_patterns)),
    path("oauth/", include("allauth.urls")),
    path("summernote/", include("django_summernote.urls")),
    path("users/", include("users.urls")),
    path("blog/", include("blog.urls")),
    path("", include("home.urls")),
    path("board/", include("board.urls")),
    path("portfolio/", include("portfolio.urls")),
    path("error/", include(error_patterns)),
    path("i18n/", include("django.conf.urls.i18n")),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="home/robots.txt", content_type="text/plain"
        ),
    ),
    path(
        "sitemap.xml",
        index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "sitemap-<section>.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # path("silk/", include("silk.urls", namespace="silk")),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    handler400 = "common.error.error_views.bad_request_page"
    handler403 = "common.error.error_views.permission_denied_page"
    handler404 = "common.error.error_views.page_not_found_page"
    handler500 = "common.error.error_views.server_error_page"
