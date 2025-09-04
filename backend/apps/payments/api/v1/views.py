from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from django.conf import settings
import time
import logging
from decimal import Decimal

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.sandbox import PaymentSandbox
from apps.payments.paypal_service import PayPalService
from .serializers import (
    ChargePaymentSerializer, PaymentResponseSerializer, 
    PaymentStatusSerializer, SandboxInfoSerializer, WebhookEventSerializer
)


logger = logging.getLogger(__name__)


# PayPal Integration Views
@extend_schema(
    tags=["payments"],
    summary="Create PayPal order",
    description="Create a PayPal payment order for checkout"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_paypal_order(request):
    """Create PayPal order for payment"""
    customer_id = getattr(request.user, 'id', None)
    if not customer_id:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify order exists and belongs to customer
        order = Order.objects.get(OrderID=order_id, CustomerID=customer_id)
        
        # Create PayPal order
        paypal_service = PayPalService()
        result = paypal_service.create_order(
            amount=order.TotalAmount,
            currency='USD',
            order_id=str(order_id)
        )
        
        if result.get('success'):
            # Find approval URL
            approval_url = None
            for link in result.get('links', []):
                if link.get('rel') == 'approve':
                    approval_url = link.get('href')
                    break
            
            # Create payment record
            payment = Payment.objects.create(
                OrderID=order_id,
                Amount=order.TotalAmount,
                PaymentMethod='paypal',
                Status='pending',
                PaypalOrderID=result.get('order_id'),
                PaymentDate=timezone.now()
            )
            
            return Response({
                'success': True,
                'paypal_order_id': result.get('order_id'),
                'approval_url': approval_url,
                'payment_id': payment.PaymentID
            })
        else:
            logger.error(f"PayPal order creation failed: {result}")
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"PayPal order creation error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["payments"],
    summary="Capture PayPal payment",
    description="Capture/finalize PayPal payment after user approval"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def capture_paypal_payment(request):
    """Capture PayPal payment after user approval"""
    customer_id = getattr(request.user, 'id', None)
    if not customer_id:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        paypal_order_id = request.data.get('paypal_order_id')
        if not paypal_order_id:
            return Response({"error": "paypal_order_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find payment record
        payment = Payment.objects.get(PaypalOrderID=paypal_order_id)
        
        # Verify order belongs to customer
        order = Order.objects.get(OrderID=payment.OrderID, CustomerID=customer_id)
        
        # Capture payment
        paypal_service = PayPalService()
        result = paypal_service.capture_order(paypal_order_id)
        
        if result.get('success'):
            # Extract capture details
            purchase_units = result.get('purchase_units', [])
            capture_info = {}
            if purchase_units:
                captures = purchase_units[0].get('payments', {}).get('captures', [])
                if captures:
                    capture_info = captures[0]
            
            # Update payment record
            payment.Status = 'completed'
            payment.TransactionID = capture_info.get('id')
            payment.PaypalPayerID = result.get('payer', {}).get('payer_id')
            payment.PaypalPaymentID = capture_info.get('id')
            payment.save()
            
            # Update order status
            order.Status = 'paid'
            order.save()
            
            return Response({
                'success': True,
                'status': 'completed',
                'transaction_id': capture_info.get('id'),
                'payment_id': payment.PaymentID
            })
        else:
            logger.error(f"PayPal capture failed: {result}")
            payment.Status = 'failed'
            payment.save()
            
            return Response({
                'success': False,
                'error': result.get('error', 'Capture failed')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"PayPal capture error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["payments"],
    summary="PayPal webhook handler",
    description="Handle PayPal webhook events for payment notifications"
)
@api_view(['POST'])
@permission_classes([AllowAny])  # PayPal webhooks don't use authentication
def paypal_webhook(request):
    """Handle PayPal webhook events"""
    try:
        # Get webhook data
        webhook_data = request.data
        event_type = webhook_data.get('event_type', '')
        resource = webhook_data.get('resource', {})
        
        logger.info(f"PayPal webhook received: {event_type}")
        
        # Handle different event types
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # Payment was successfully captured
            paypal_order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
            capture_id = resource.get('id')
            
            if paypal_order_id:
                try:
                    payment = Payment.objects.get(PaypalOrderID=paypal_order_id)
                    payment.Status = 'completed'
                    payment.TransactionID = capture_id
                    payment.save()
                    
                    # Update order status
                    if payment.OrderID:
                        try:
                            order = Order.objects.get(OrderID=payment.OrderID)
                            order.Status = 'paid'
                            order.save()
                        except Order.DoesNotExist:
                            pass
                    
                    logger.info(f"Payment updated via webhook: {payment.PaymentID}")
                except Payment.DoesNotExist:
                    logger.warning(f"Payment not found for PayPal order: {paypal_order_id}")
        
        elif event_type == 'PAYMENT.CAPTURE.DENIED':
            # Payment was denied
            paypal_order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
            
            if paypal_order_id:
                try:
                    payment = Payment.objects.get(PaypalOrderID=paypal_order_id)
                    payment.Status = 'failed'
                    payment.save()
                    
                    logger.info(f"Payment marked as failed via webhook: {payment.PaymentID}")
                except Payment.DoesNotExist:
                    logger.warning(f"Payment not found for PayPal order: {paypal_order_id}")
        
        return Response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"PayPal webhook error: {e}")
        return Response({'error': 'Webhook processing failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ...existing code...


@extend_schema(
    tags=["payments"],
    request=ChargePaymentSerializer,
    responses={200: PaymentResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def charge_payment(request):
    """
    Process payment for an order using sandbox gateway
    
    Supports multiple payment methods with realistic sandbox behavior:
    - Credit/Debit cards with test card numbers
    - PayPal simulation
    - Bank transfers
    - E-wallets  
    - Cash on delivery
    
    Use test card 4111111111111111 for successful payments
    Use test card 4000000000000002 for declined payments
    """
    customer_id = getattr(request.user, 'id', None)
    if not customer_id:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = ChargePaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    data = serializer.validated_data
    order_id = data['order_id']
    payment_method = data['payment_method']
    
    # Verify order exists and belongs to customer
    try:
        order = Order.objects.get(OrderID=order_id, CustomerID=customer_id)
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if order is payable
    if order.Status not in ['pending', 'confirmed']:
        return Response(
            {"error": f"Cannot process payment for order with status: {order.Status}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check for existing successful payment
    existing_payment = Payment.objects.filter(
        OrderID=order_id, 
        Status__in=['completed', 'processing']
    ).first()
    if existing_payment:
        return Response(
            {"error": "Payment already processed for this order"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Process payment through sandbox
    sandbox_kwargs = {
        'currency': data.get('currency', 'VND'),
        'description': data.get('description', f'Order #{order_id} payment'),
        'customer_id': customer_id,
        'order_id': order_id
    }
    
    # Add payment method specific data
    if payment_method in ['credit_card', 'debit_card']:
        sandbox_kwargs.update({
            'card_holder': data.get('card_holder'),
            'card_expiry': data.get('card_expiry'),
            'card_cvv': data.get('card_cvv')
        })
    elif payment_method == 'paypal':
        sandbox_kwargs['paypal_email'] = data.get('paypal_email')
    elif payment_method == 'bank_transfer':
        sandbox_kwargs['bank_account'] = data.get('bank_account')
    elif payment_method == 'e_wallet':
        sandbox_kwargs['wallet_phone'] = data.get('wallet_phone')
    
    # Simulate processing delay if configured
    if getattr(settings, 'PAYMENT_GATEWAY', {}).get('SIMULATE_DELAYS', False):
        processing_time = PaymentSandbox.PAYMENT_METHODS.get(payment_method, {}).get('processing_time', (1, 3))
        delay = min(processing_time) if payment_method == 'cash_on_delivery' else 1
        if delay > 0:
            time.sleep(delay)
    
    # Process the payment
    try:
        payment_result = PaymentSandbox.process_payment(
            amount=order.TotalAmount,
            payment_method=payment_method,
            card_number=data.get('card_number'),
            **sandbox_kwargs
        )
    except Exception as e:
        return Response(
            {"error": f"Payment processing failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Create payment record
    payment = Payment(
        OrderID=order_id,
        Amount=order.TotalAmount,
        PaymentMethod=payment_method,
        Status=payment_result['status'],
        TransactionID=payment_result.get('transaction_id', ''),
        SandboxPaymentID=payment_result.get('payment_id', ''),
        PaymentDate=payment_result['processed_at']
    )
    payment.save()
    
    # Update order status based on payment result
    if payment_result.get('success') is True:
        order.Status = 'confirmed'
        order.save()
    elif payment_result.get('success') is False:
        order.Status = 'payment_failed'
        order.save()
    
    # Prepare response data
    response_data = {
        'payment_id': payment_result['payment_id'],
        'order_id': order_id,
        'amount': payment.Amount,
        'currency': payment_result.get('currency', 'VND'),
        'payment_method': payment.PaymentMethod,
        'status': payment.Status,
        'transaction_id': payment.TransactionID,
        'payment_date': payment.PaymentDate,
        'message': payment_result.get('message', 'Payment processed'),
        'sandbox_mode': True,
        'processing_time': payment_result.get('processing_time', 0)
    }
    
    # Add payment method specific response fields
    for field in ['card_type', 'card_last4', 'error_code', 'decline_code', 
                  'paypal_transaction_id', 'bank_reference', 'wallet_transaction_id']:
        if field in payment_result:
            response_data[field] = payment_result[field]
    
    response_serializer = PaymentResponseSerializer(response_data)
    return Response(response_serializer.data)


@extend_schema(
    tags=["payments"],
    responses={200: PaymentStatusSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status(request, payment_id):
    """Get payment status by payment ID"""
    customer_id = getattr(request.user, 'id', None)
    if not customer_id:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Try to find by sandbox payment ID first, then by database ID
        if payment_id.startswith('pay_'):
            payment = Payment.objects.filter(SandboxPaymentID=payment_id).first()
        else:
            # Numeric ID, search by PaymentID
            payment = Payment.objects.filter(PaymentID=int(payment_id)).first()
        
        if not payment:
            raise Payment.DoesNotExist()
            
        # Verify payment belongs to customer's order
        order = Order.objects.get(OrderID=payment.OrderID, CustomerID=customer_id)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return Response(
            {"error": "Payment not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    status_messages = {
        'pending': 'Payment is being processed',
        'processing': 'Payment is in progress',
        'completed': 'Payment completed successfully',
        'failed': 'Payment failed',
        'refunded': 'Payment has been refunded',
        'requires_action': 'Payment requires additional action'
    }
    
    response_data = {
        'payment_id': str(payment.PaymentID),
        'status': payment.Status,
        'transaction_id': payment.TransactionID or '',
        'payment_date': payment.PaymentDate,
        'message': status_messages.get(payment.Status, 'Unknown status')
    }
    
    serializer = PaymentStatusSerializer(response_data)
    return Response(serializer.data)


@extend_schema(
    tags=["payments"],
    responses={200: PaymentStatusSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_payment(request, order_id):
    """Get payment info for an order"""
    customer_id = getattr(request.user, 'id', None)
    if not customer_id:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        order = Order.objects.get(OrderID=order_id, CustomerID=customer_id)
        payment = Payment.objects.filter(OrderID=order_id).first()
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not payment:
        return Response(
            {"error": "No payment found for this order"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    status_messages = {
        'pending': 'Payment is being processed',
        'processing': 'Payment is in progress',
        'completed': 'Payment completed successfully',
        'failed': 'Payment failed',
        'refunded': 'Payment has been refunded',
        'requires_action': 'Payment requires additional action'
    }
    
    response_data = {
        'payment_id': str(payment.PaymentID),
        'status': payment.Status,
        'transaction_id': payment.TransactionID or '',
        'payment_date': payment.PaymentDate,
        'message': status_messages.get(payment.Status, 'Unknown status')
    }
    
    serializer = PaymentStatusSerializer(response_data)
    return Response(serializer.data)


@extend_schema(
    tags=["payments"],
    responses={200: SandboxInfoSerializer},
    summary="Get sandbox testing information",
    description="Returns information about test cards, supported methods, and sandbox capabilities"
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_sandbox_info(request):
    """
    Get information about sandbox testing capabilities
    
    Returns test card numbers, supported payment methods, and sandbox configuration
    """
    test_cards_info = PaymentSandbox.get_test_cards_info()
    
    response_data = {
        'sandbox_mode': getattr(settings, 'PAYMENT_GATEWAY', {}).get('SANDBOX_MODE', True),
        'test_cards': test_cards_info,
        'supported_methods': list(PaymentSandbox.PAYMENT_METHODS.keys()),
        'webhook_url': f"{request.scheme}://{request.get_host()}/api/v1/payments/webhooks/"
    }
    
    serializer = SandboxInfoSerializer(response_data)
    return Response(serializer.data)


@extend_schema(
    tags=["payments"],
    request=WebhookEventSerializer,
    responses={200: dict},
    summary="Simulate webhook event",
    description="Simulate a payment webhook event for testing purposes"
)
@api_view(['POST'])
def simulate_webhook(request, payment_id):
    """
    Simulate a webhook event for testing
    
    This endpoint allows you to simulate various payment events:
    - payment.completed
    - payment.failed  
    - payment.refunded
    - payment.disputed
    """
    event_type = request.data.get('event_type', 'payment.completed')
    
    # Generate webhook data
    webhook_data = PaymentSandbox.simulate_webhook(payment_id, event_type)
    
    # In a real implementation, this would be sent to your webhook endpoint
    # For sandbox, we just return the webhook data that would be sent
    
    return Response({
        'message': f'Webhook simulation for {event_type}',
        'webhook_data': webhook_data,
        'note': 'In production, this data would be POSTed to your webhook endpoint'
    })
