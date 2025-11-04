from django.contrib.sitemaps import Sitemap
from .models import rest_framework, accounts, generator

class Rest_frameworkSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return rest_framework.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Or the relevant datetime field


class AccountsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return accounts.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Adjust if you use a different timestamp field

    def location(self, obj):
        return obj.get_absolute_url()  # You need get_absolute_url() on this model too

class GeneratorSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return generator.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Adjust if you use a different timestamp field

    def location(self, obj):
        return obj.get_absolute_url()  # You need get_absolute_url() on this model too
