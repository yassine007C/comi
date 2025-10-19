from django.db import models
from django.contrib.auth.models import User


class TokenPackage(models.Model):
    name = models.CharField(max_length=100)
    token_amount = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - {self.token_amount} tokens (${self.price})"


class TokenPurchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_purchases')
    package = models.ForeignKey(TokenPackage, on_delete=models.SET_NULL, null=True)
    token_amount = models.IntegerField()
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.token_amount} tokens - {self.status}"

    def complete_purchase(self):
        from django.utils import timezone
        if self.status == 'pending':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.user.profile.add_tokens(self.token_amount)
            self.save()
