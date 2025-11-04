from django.contrib.sitemaps import Sitemap

from accounts.models import UserProfile



class AccountsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return UserProfile.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # Provide absolute URL for UserProfile pages. 
        # If UserProfile doesn't have get_absolute_url, define here:
        return f"/accounts/profile/{obj.user.username}/"  # Adjust as per your URL pattern



