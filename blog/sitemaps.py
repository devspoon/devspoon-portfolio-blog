from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import ProjectPost, OnlineStudyPost, BlogPost, OpenSourcePost, BooksPost


class ProjectPostListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            reverse("blog:project_list")
        ]  # Assuming the URL name for list view is 'list'

    def location(self, item):
        return item


class ProjectPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return ProjectPost.objects.all()

    def location(self, obj):
        return reverse(
            "blog:project_detail", args=[obj.pk]
        )  # Assuming the URL name for detail view is 'detail'

    def lastmod(self, obj):
        return obj.updated_at


class OnlineStudyPostListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            reverse("blog:online_study_list")
        ]  # Assuming the URL name for list view is 'list'

    def location(self, item):
        return item


class OnlineStudyPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return OnlineStudyPost.objects.all()

    def location(self, obj):
        return reverse(
            "blog:online_study_detail", args=[obj.pk]
        )  # Assuming the URL name for detail view is 'detail'

    def lastmod(self, obj):
        return obj.updated_at


class BlogPostListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            reverse("blog:blog_list")
        ]  # Assuming the URL name for list view is 'list'

    def location(self, item):
        return item


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return BlogPost.objects.all()

    def location(self, obj):
        return reverse(
            "blog:blog_detail", args=[obj.pk]
        )  # Assuming the URL name for detail view is 'detail'

    def lastmod(self, obj):
        return obj.updated_at


class OpenSourcePostListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            reverse("blog:opensource_list")
        ]  # Assuming the URL name for list view is 'list'

    def location(self, item):
        return item


class OpenSourcePostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return OpenSourcePost.objects.all()

    def location(self, obj):
        return reverse(
            "blog:opensource_detail", args=[obj.pk]
        )  # Assuming the URL name for detail view is 'detail'

    def lastmod(self, obj):
        return obj.updated_at


class BooksPostListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            reverse("blog:books_list")
        ]  # Assuming the URL name for list view is 'list'

    def location(self, item):
        return item


class BooksPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return BooksPost.objects.all()

    def location(self, obj):
        return reverse(
            "blog:books_detail", args=[obj.pk]
        )  # Assuming the URL name for detail view is 'detail'

    def lastmod(self, obj):
        return obj.updated_at
