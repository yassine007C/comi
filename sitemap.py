from django.contrib.sitemaps import Sitemap
from .models import Rest_framework, Accounts, Generator

class Rest_frameworkSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Rest_framework.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Or the relevant datetime field


class Accounts(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return UserProfile.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Adjust if you use a different timestamp field

    def location(self, obj):
        return obj.get_absolute_url()  # You need get_absolute_url() on this model too

class Generator(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Generator.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Adjust if you use a different timestamp field

    def location(self, obj):
        return obj.get_absolute_url()  # You need get_absolute_url() on this model too
