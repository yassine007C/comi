from django.contrib import admin
from .models import TokenPackage, TokenPurchase


@admin.register(TokenPackage)
class TokenPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'token_amount', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active']


@admin.register(TokenPurchase)
class TokenPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_amount', 'price_paid', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'stripe_payment_intent_id']
    readonly_fields = ['created_at', 'completed_at']
