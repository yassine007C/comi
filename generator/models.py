from django.db import models
from django.contrib.auth.models import User


class GeneratedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_images')
    context = models.TextField()
    dialogue = models.JSONField()
    target_line = models.CharField(max_length=500)
    speaker = models.CharField(max_length=100)
    image_url = models.URLField(max_length=1000)
    tokens_used = models.IntegerField(default=1)
    subject_description = models.TextField(blank=True)
    setting_and_scene = models.TextField(blank=True)
    action_or_expression = models.TextField(blank=True)
    camera_and_style = models.TextField(blank=True)
    full_image_prompt = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.speaker} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
