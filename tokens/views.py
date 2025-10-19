from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import TokenPackage, TokenPurchase
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def token_packages_view(request):
    packages = TokenPackage.objects.filter(is_active=True)
    return render(request, 'tokens/packages.html', {
        'packages': packages,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })


@login_required
@require_POST
def create_checkout_session(request):
    try:
        data = json.loads(request.body)
        package_id = data.get('package_id')
        package = get_object_or_404(TokenPackage, id=package_id, is_active=True)
        
        if not settings.STRIPE_SECRET_KEY:
            return JsonResponse({'error': 'Stripe is not configured'}, status=400)
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(package.price * 100),
                    'product_data': {
                        'name': package.name,
                        'description': f'{package.token_amount} tokens for image generation',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/tokens/success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/tokens/packages/'),
            client_reference_id=str(request.user.id),
            metadata={
                'package_id': package.id,
                'user_id': request.user.id,
                'token_amount': package.token_amount,
            }
        )
        
        purchase = TokenPurchase.objects.create(
            user=request.user,
            package=package,
            token_amount=package.token_amount,
            price_paid=package.price,
            stripe_session_id=checkout_session.id,
            status='pending'
        )
        
        return JsonResponse({'sessionId': checkout_session.id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def purchase_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                purchase = TokenPurchase.objects.filter(
                    stripe_session_id=session_id,
                    user=request.user
                ).first()
                
                if purchase and purchase.status == 'pending':
                    purchase.complete_purchase()
                    messages.success(
                        request,
                        f'Payment successful! {purchase.token_amount} tokens have been added to your account.'
                    )
        except Exception as e:
            messages.error(request, 'Error processing payment. Please contact support.')
    
    return redirect('generator:dashboard')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse(status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        try:
            purchase = TokenPurchase.objects.get(stripe_session_id=session['id'])
            if purchase.status == 'pending':
                purchase.complete_purchase()
        except TokenPurchase.DoesNotExist:
            pass
    
    return HttpResponse(status=200)


@login_required
def purchase_history(request):
    purchases = TokenPurchase.objects.filter(user=request.user)
    return render(request, 'tokens/history.html', {'purchases': purchases})
