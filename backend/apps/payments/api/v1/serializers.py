from rest_framework import serializers


class ChargePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=[
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Bank Transfer'),
            ('e_wallet', 'E-Wallet'),
            ('cash_on_delivery', 'Cash on Delivery')
        ]
    )
    
    # Card payment fields
    card_number = serializers.CharField(
        max_length=19, required=False, allow_blank=True,
        help_text="Use test cards: 4111111111111111 (success), 4000000000000002 (decline)"
    )
    card_holder = serializers.CharField(max_length=255, required=False, allow_blank=True)
    card_expiry = serializers.CharField(
        max_length=7, required=False, allow_blank=True,
        help_text="Format: MM/YYYY"
    )
    card_cvv = serializers.CharField(
        max_length=4, required=False, allow_blank=True,
        help_text="Use any 3-4 digits for sandbox"
    )
    
    # Alternative payment fields
    paypal_email = serializers.EmailField(required=False, allow_blank=True)
    bank_account = serializers.CharField(max_length=50, required=False, allow_blank=True)
    wallet_phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    
    # Optional metadata
    currency = serializers.CharField(max_length=3, default='VND')
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    def validate(self, data):
        payment_method = data.get('payment_method')
        
        # Validate required fields based on payment method
        if payment_method in ['credit_card', 'debit_card']:
            if not data.get('card_number'):
                raise serializers.ValidationError("Card number is required for card payments")
            if not data.get('card_holder'):
                raise serializers.ValidationError("Card holder name is required")
                
        elif payment_method == 'paypal':
            if not data.get('paypal_email'):
                raise serializers.ValidationError("PayPal email is required")
                
        elif payment_method == 'bank_transfer':
            if not data.get('bank_account'):
                raise serializers.ValidationError("Bank account is required")
                
        elif payment_method == 'e_wallet':
            if not data.get('wallet_phone'):
                raise serializers.ValidationError("Wallet phone number is required")
        
        return data


class PaymentResponseSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    order_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    payment_method = serializers.CharField()
    status = serializers.CharField()
    transaction_id = serializers.CharField(allow_blank=True)
    payment_date = serializers.DateTimeField()
    message = serializers.CharField()
    
    # Sandbox-specific fields
    sandbox_mode = serializers.BooleanField(default=True)
    processing_time = serializers.IntegerField(required=False)
    
    # Card-specific fields
    card_type = serializers.CharField(required=False)
    card_last4 = serializers.CharField(required=False)
    
    # Error fields for failed payments
    error_code = serializers.CharField(required=False)
    decline_code = serializers.CharField(required=False)
    
    # Additional payment method info
    paypal_transaction_id = serializers.CharField(required=False)
    bank_reference = serializers.CharField(required=False)
    wallet_transaction_id = serializers.CharField(required=False)


class PaymentStatusSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    status = serializers.CharField()
    transaction_id = serializers.CharField(allow_blank=True)
    payment_date = serializers.DateTimeField()
    message = serializers.CharField()
    
    # Additional status info
    processing_time = serializers.IntegerField(required=False)
    error_code = serializers.CharField(required=False)
    decline_code = serializers.CharField(required=False)


class SandboxInfoSerializer(serializers.Serializer):
    """Information about sandbox testing capabilities"""
    sandbox_mode = serializers.BooleanField()
    test_cards = serializers.JSONField()
    supported_methods = serializers.ListField(child=serializers.CharField())
    webhook_url = serializers.URLField(required=False)
    
    
class WebhookEventSerializer(serializers.Serializer):
    """Webhook event data structure"""
    id = serializers.CharField()
    type = serializers.CharField()
    created = serializers.IntegerField()
    data = serializers.JSONField()
    livemode = serializers.BooleanField()
