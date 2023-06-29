from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Notice, Visiter, Reactivation


class NoticeListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            reverse("board:notice_list")
        ]  # Assuming the URL name for list view is 'list'

    def location(self, item):
        return item


class NoticeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Notice.objects.all()

    def location(self, obj):
        return reverse(
            "board:notice_detail", args=[obj.pk]
        )  # Assuming the URL name for detail view is 'detail'

    def lastmod(self, obj):
        return obj.updated_at


class VisiterListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            reverse("board:visiter_list")
        ]  # Assuming the URL name for list view is 'list'

    def location(self, item):
        return item


class VisiterSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Visiter.objects.all()

    def location(self, obj):
        return reverse(
            "board:visiter_detail", args=[obj.pk]
        )  # Assuming the URL name for detail view is 'detail'

    def lastmod(self, obj):
        return obj.updated_at


class ReactivationListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            reverse("board:reactivation_list")
        ]  # Assuming the URL name for list view is 'list'

    def location(self, item):
        return item


class ReactivationSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Reactivation.objects.all()

    def location(self, obj):
        return reverse(
            "board:reactivation_detail", args=[obj.pk]
        )  # Assuming the URL name for detail view is 'detail'

    def lastmod(self, obj):
        return obj.updated_at
