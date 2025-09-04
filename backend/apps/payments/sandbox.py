"""
Payment Sandbox Configuration and Utilities
Provides realistic payment testing without real transactions
"""
import uuid
import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone


class PaymentSandbox:
    """Sandbox payment gateway for testing"""
    
    # Test card numbers and their expected behaviors
    TEST_CARDS = {
        # Successful cards
        '4111111111111111': {'type': 'visa', 'behavior': 'success', 'description': 'Visa - Always succeeds'},
        '5555555555554444': {'type': 'mastercard', 'behavior': 'success', 'description': 'Mastercard - Always succeeds'},
        '2223000048400011': {'type': 'mastercard', 'behavior': 'success', 'description': 'Mastercard - Always succeeds'},
        '378282246310005': {'type': 'amex', 'behavior': 'success', 'description': 'American Express - Always succeeds'},
        '4242424242424242': {'type': 'visa', 'behavior': 'success', 'description': 'Stripe test card - Always succeeds'},
        
        # Decline cards
        '4000000000000002': {'type': 'visa', 'behavior': 'decline_generic', 'description': 'Generic decline'},
        '4000000000000069': {'type': 'visa', 'behavior': 'decline_expired', 'description': 'Expired card'},
        '4000000000000119': {'type': 'visa', 'behavior': 'decline_processing', 'description': 'Processing error'},
        '4000000000000127': {'type': 'visa', 'behavior': 'decline_insufficient_funds', 'description': 'Insufficient funds'},
        
        # Special behavior cards
        '4000000000000341': {'type': 'visa', 'behavior': 'require_authentication', 'description': 'Requires 3D Secure'},
        '4000000000009995': {'type': 'visa', 'behavior': 'slow_processing', 'description': 'Slow processing (5+ seconds)'},
    }
    
    # Payment method configurations
    PAYMENT_METHODS = {
        'credit_card': {
            'success_rate': 0.95,
            'processing_time': (1, 3),  # seconds
            'supported_currencies': ['USD', 'EUR', 'VND']
        },
        'debit_card': {
            'success_rate': 0.93,
            'processing_time': (1, 4),
            'supported_currencies': ['USD', 'EUR', 'VND']
        },
        'paypal': {
            'success_rate': 0.98,
            'processing_time': (2, 5),
            'supported_currencies': ['USD', 'EUR', 'VND']
        },
        'bank_transfer': {
            'success_rate': 0.99,
            'processing_time': (10, 30),
            'supported_currencies': ['VND', 'USD']
        },
        'e_wallet': {
            'success_rate': 0.97,
            'processing_time': (1, 2),
            'supported_currencies': ['VND']
        },
        'cash_on_delivery': {
            'success_rate': 1.0,
            'processing_time': (0, 1),
            'supported_currencies': ['VND']
        }
    }
    
    @classmethod
    def process_payment(cls, amount, payment_method, card_number=None, **kwargs):
        """
        Process a sandbox payment
        Returns a payment result dictionary
        """
        result = {
            'payment_id': f'pay_sandbox_{uuid.uuid4().hex[:16]}',
            'transaction_id': f'txn_{uuid.uuid4().hex[:12].upper()}',
            'amount': amount,
            'currency': kwargs.get('currency', 'VND'),
            'payment_method': payment_method,
            'processed_at': timezone.now(),
            'processing_time': 0,
            'metadata': {}
        }
        
        # Handle card payments with test card behaviors
        if payment_method in ['credit_card', 'debit_card'] and card_number:
            return cls._process_card_payment(result, card_number, **kwargs)
        
        # Handle other payment methods
        return cls._process_other_payment(result, payment_method, **kwargs)
    
    @classmethod
    def _process_card_payment(cls, result, card_number, **kwargs):
        """Process card payment with test card behaviors"""
        card_number = str(card_number).replace(' ', '').replace('-', '')
        
        if card_number in cls.TEST_CARDS:
            card_info = cls.TEST_CARDS[card_number]
            result['card_type'] = card_info['type']
            result['card_last4'] = card_number[-4:]
            
            behavior = card_info['behavior']
            
            if behavior == 'success':
                result.update({
                    'status': 'completed',
                    'success': True,
                    'message': 'Payment completed successfully',
                    'processing_time': random.randint(1, 3)
                })
                
            elif behavior == 'decline_generic':
                result.update({
                    'status': 'failed',
                    'success': False,
                    'error_code': 'card_declined',
                    'message': 'Your card was declined',
                    'decline_code': 'generic_decline'
                })
                
            elif behavior == 'decline_expired':
                result.update({
                    'status': 'failed',
                    'success': False,
                    'error_code': 'expired_card',
                    'message': 'Your card has expired',
                    'decline_code': 'expired_card'
                })
                
            elif behavior == 'decline_insufficient_funds':
                result.update({
                    'status': 'failed',
                    'success': False,
                    'error_code': 'insufficient_funds',
                    'message': 'Insufficient funds',
                    'decline_code': 'insufficient_funds'
                })
                
            elif behavior == 'require_authentication':
                result.update({
                    'status': 'requires_action',
                    'success': False,
                    'message': '3D Secure authentication required',
                    'next_action': {
                        'type': 'redirect_to_url',
                        'redirect_url': f'/sandbox/3d-secure/{result["payment_id"]}'
                    }
                })
                
            elif behavior == 'slow_processing':
                result.update({
                    'status': 'processing',
                    'success': None,
                    'message': 'Payment is being processed',
                    'processing_time': random.randint(5, 15)
                })
                
        else:
            # Unknown card - simulate based on payment method success rate
            method_config = cls.PAYMENT_METHODS.get(result['payment_method'], {'success_rate': 0.9})
            if random.random() < method_config['success_rate']:
                result.update({
                    'status': 'completed',
                    'success': True,
                    'message': 'Payment completed successfully',
                    'card_last4': card_number[-4:],
                    'processing_time': random.randint(*method_config.get('processing_time', (1, 3)))
                })
            else:
                result.update({
                    'status': 'failed',
                    'success': False,
                    'error_code': 'card_declined',
                    'message': 'Your card was declined',
                    'decline_code': 'generic_decline'
                })
        
        return result
    
    @classmethod
    def _process_other_payment(cls, result, payment_method, **kwargs):
        """Process non-card payments"""
        method_config = cls.PAYMENT_METHODS.get(payment_method, {'success_rate': 0.9})
        processing_time = random.randint(*method_config.get('processing_time', (1, 3)))
        
        if random.random() < method_config['success_rate']:
            if payment_method == 'paypal':
                result.update({
                    'status': 'completed',
                    'success': True,
                    'message': 'PayPal payment completed',
                    'paypal_transaction_id': f'PAYPAL{uuid.uuid4().hex[:16].upper()}',
                    'processing_time': processing_time
                })
                
            elif payment_method == 'bank_transfer':
                result.update({
                    'status': 'processing' if processing_time > 5 else 'completed',
                    'success': True if processing_time <= 5 else None,
                    'message': 'Bank transfer initiated' if processing_time > 5 else 'Bank transfer completed',
                    'bank_reference': f'BT{uuid.uuid4().hex[:12].upper()}',
                    'processing_time': processing_time
                })
                
            elif payment_method == 'e_wallet':
                result.update({
                    'status': 'completed',
                    'success': True,
                    'message': 'E-wallet payment completed',
                    'wallet_transaction_id': f'EW{uuid.uuid4().hex[:14].upper()}',
                    'processing_time': processing_time
                })
                
            elif payment_method == 'cash_on_delivery':
                result.update({
                    'status': 'pending',
                    'success': None,
                    'message': 'Cash on delivery order created',
                    'processing_time': 0,
                    'expected_delivery': timezone.now() + timedelta(days=random.randint(1, 3))
                })
                
        else:
            # Payment failed
            error_messages = {
                'paypal': 'PayPal payment was not approved',
                'bank_transfer': 'Bank transfer rejected by your bank',
                'e_wallet': 'E-wallet payment failed - insufficient balance'
            }
            
            result.update({
                'status': 'failed',
                'success': False,
                'message': error_messages.get(payment_method, 'Payment method declined'),
                'error_code': 'payment_declined'
            })
            
        return result
    
    @classmethod
    def get_test_cards_info(cls):
        """Return information about test cards for documentation"""
        return {
            'success_cards': [
                {
                    'number': card,
                    'type': info['type'],
                    'description': info['description']
                }
                for card, info in cls.TEST_CARDS.items()
                if info['behavior'] == 'success'
            ],
            'decline_cards': [
                {
                    'number': card,
                    'type': info['type'],
                    'description': info['description']
                }
                for card, info in cls.TEST_CARDS.items()
                if info['behavior'].startswith('decline_')
            ],
            'special_cards': [
                {
                    'number': card,
                    'type': info['type'],
                    'description': info['description']
                }
                for card, info in cls.TEST_CARDS.items()
                if not info['behavior'].startswith('decline_') and info['behavior'] != 'success'
            ]
        }
    
    @classmethod
    def simulate_webhook(cls, payment_id, event_type='payment.completed'):
        """
        Simulate a webhook event for testing
        Returns webhook data that would be sent to your endpoint
        """
        webhook_data = {
            'id': f'evt_sandbox_{uuid.uuid4().hex[:16]}',
            'object': 'event',
            'api_version': '2023-10-16',
            'created': int(timezone.now().timestamp()),
            'type': event_type,
            'data': {
                'object': {
                    'id': payment_id,
                    'object': 'payment_intent',
                    'status': event_type.split('.')[1],
                    'amount': 100000,  # This would be the actual amount
                    'currency': 'vnd',
                    'created': int(timezone.now().timestamp()),
                    'metadata': {}
                }
            },
            'livemode': False,  # Always false for sandbox
            'pending_webhooks': 1,
            'request': {
                'id': f'req_sandbox_{uuid.uuid4().hex[:16]}',
                'idempotency_key': None
            }
        }
        
        return webhook_data
