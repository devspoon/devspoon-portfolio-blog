from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class Portfolioitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            reverse("portfolio:portfolio")
        ]  # Assuming the URL name for list view is 'list'

    def location(self, item):
        return item
