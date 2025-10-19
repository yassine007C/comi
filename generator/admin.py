from django.contrib import admin
from .models import GeneratedImage


@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ['user', 'speaker', 'target_line', 'tokens_used', 'created_at']
    list_filter = ['created_at', 'tokens_used']
    search_fields = ['user__username', 'speaker', 'target_line']
    readonly_fields = ['created_at']
