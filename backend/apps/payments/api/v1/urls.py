from django.urls import path
from .views import (
    charge_payment, get_payment_status, get_order_payment,
    get_sandbox_info, simulate_webhook,
    create_paypal_order, capture_paypal_payment, paypal_webhook
)

urlpatterns = [
    # PayPal integration
    path('paypal/create-order/', create_paypal_order, name='create-paypal-order'),
    path('paypal/capture/', capture_paypal_payment, name='capture-paypal-payment'),
    path('paypal/webhook/', paypal_webhook, name='paypal-webhook'),
    
    # Legacy payment processing
    path('charge/', charge_payment, name='charge-payment'),
    path('<str:payment_id>/status/', get_payment_status, name='payment-status'),
    path('order/<int:order_id>/', get_order_payment, name='order-payment'),
    
    # Sandbox features
    path('sandbox/info/', get_sandbox_info, name='sandbox-info'),
    path('sandbox/webhook/<str:payment_id>/', simulate_webhook, name='simulate-webhook'),
]
