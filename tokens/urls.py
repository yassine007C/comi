from django.urls import path
from . import views

app_name = 'tokens'

urlpatterns = [
    path('packages/', views.token_packages_view, name='packages'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.purchase_success, name='success'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('history/', views.purchase_history, name='history'),
]
