from django.contrib.sitemaps import Sitemap
from generator.models import GeneratedImage
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


class GeneratedImageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return GeneratedImage.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        # If you have a URL pattern for each generated image, use it here.
        # If you don't have get_absolute_url on GeneratedImage, define your URL manually. Example:
        return f"/generated_images/{obj.pk}/"
