# Payment Sandbox Documentation

## Overview

The Payment Sandbox provides a comprehensive testing environment for payment processing without real transactions. It simulates realistic payment gateway behavior including success/failure scenarios, processing delays, and various payment methods.

## Features

### ✅ **Supported Payment Methods**
- **Credit/Debit Cards** - Visa, Mastercard, Amex with test card numbers
- **PayPal** - Email-based payment simulation  
- **Bank Transfer** - Account-based transfers with processing delays
- **E-Wallet** - Phone number-based wallet payments
- **Cash on Delivery** - Order-first, pay-later simulation

### 🧪 **Test Card Numbers**

#### Success Cards (Always Approved)
```
4111111111111111 - Visa (Generic success)
4000000000000002 - Visa (Always succeeds) 
5555555555554444 - Mastercard (Always succeeds)
2223000048400011 - Mastercard (Always succeeds)
378282246310005  - American Express (Always succeeds)
4242424242424242 - Visa (Stripe-style test card)
```

#### Decline Cards (Always Rejected)
```
4000000000000002 - Generic decline
4000000000000069 - Expired card
4000000000000119 - Processing error
4000000000000127 - Insufficient funds
```

#### Special Behavior Cards
```
4000000000000341 - Requires 3D Secure authentication
4000000000009995 - Slow processing (5+ seconds)
```

## API Endpoints

### 1. Process Payment
```http
POST /api/v1/payments/charge/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "order_id": 123,
  "payment_method": "credit_card",
  "card_number": "4111111111111111",
  "card_holder": "John Doe",
  "card_expiry": "12/2025",
  "card_cvv": "123",
  "currency": "VND"
}
```

### 2. Check Payment Status
```http
GET /api/v1/payments/{payment_id}/status/
Authorization: Bearer <jwt_token>
```

### 3. Get Order Payment
```http
GET /api/v1/payments/order/{order_id}/
Authorization: Bearer <jwt_token>
```

### 4. Get Sandbox Information
```http
GET /api/v1/payments/sandbox/info/
```

### 5. Simulate Webhook Event
```http
POST /api/v1/payments/sandbox/webhook/{payment_id}/
Content-Type: application/json

{
  "event_type": "payment.completed"
}
```

## Payment Method Examples

### Credit Card Payment
```json
{
  "order_id": 123,
  "payment_method": "credit_card",
  "card_number": "4111111111111111",
  "card_holder": "John Doe",
  "card_expiry": "12/2025",
  "card_cvv": "123"
}
```

### PayPal Payment
```json
{
  "order_id": 123,
  "payment_method": "paypal",
  "paypal_email": "user@example.com"
}
```

### Bank Transfer
```json
{
  "order_id": 123,
  "payment_method": "bank_transfer",
  "bank_account": "1234567890"
}
```

### E-Wallet Payment
```json
{
  "order_id": 123,
  "payment_method": "e_wallet",
  "wallet_phone": "+84901234567"
}
```

### Cash on Delivery
```json
{
  "order_id": 123,
  "payment_method": "cash_on_delivery"
}
```

## Response Format

### Successful Payment Response
```json
{
  "payment_id": "pay_sandbox_abc123",
  "order_id": 123,
  "amount": "150000.00",
  "currency": "VND",
  "payment_method": "credit_card",
  "status": "completed",
  "transaction_id": "TXN_SANDBOX123",
  "payment_date": "2025-08-29T10:00:00Z",
  "message": "Payment completed successfully",
  "sandbox_mode": true,
  "processing_time": 2,
  "card_type": "visa",
  "card_last4": "1111"
}
```

### Failed Payment Response
```json
{
  "payment_id": "pay_sandbox_def456",
  "order_id": 123,
  "amount": "150000.00",
  "currency": "VND",
  "payment_method": "credit_card",
  "status": "failed",
  "transaction_id": "",
  "payment_date": "2025-08-29T10:00:00Z",
  "message": "Your card was declined",
  "sandbox_mode": true,
  "error_code": "card_declined",
  "decline_code": "generic_decline",
  "card_last4": "0002"
}
```

## Payment Statuses

- **`pending`** - Payment initiated, awaiting processing
- **`processing`** - Payment being processed by gateway
- **`completed`** - Payment successful
- **`failed`** - Payment failed/declined
- **`requires_action`** - Additional authentication needed
- **`refunded`** - Payment has been refunded

## Environment Configuration

Add these variables to your `.env` file:

```env
# Payment Sandbox Settings
PAYMENT_SANDBOX_MODE=1
PAYMENT_API_KEY=sandbox_test_key_12345
PAYMENT_WEBHOOK_SECRET=sandbox_webhook_secret_67890
PAYMENT_SIMULATE_DELAYS=1
PAYMENT_LOG_REQUESTS=1
PAYMENT_TIMEOUT=30
```

## Testing Scenarios

### 1. Successful Flow
1. Use test card `4111111111111111`
2. Expect `status: "completed"`
3. Order status updates to `"confirmed"`

### 2. Declined Payment
1. Use test card `4000000000000002`
2. Expect `status: "failed"`
3. Order status updates to `"payment_failed"`

### 3. Slow Processing
1. Use test card `4000000000009995`
2. Expect `status: "processing"`
3. Simulates real-world processing delays

### 4. Authentication Required
1. Use test card `4000000000000341`
2. Expect `status: "requires_action"`
3. Returns 3D Secure redirect URL

## Webhook Simulation

Simulate payment events for testing webhook handlers:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/payments/sandbox/webhook/pay_123/ \
  -H "Content-Type: application/json" \
  -d '{"event_type": "payment.completed"}'
```

Available event types:
- `payment.completed`
- `payment.failed`
- `payment.refunded`
- `payment.disputed`

## Integration Example

```python
import requests

# 1. Create order first
order_response = requests.post('/api/v1/orders/', {
    'from_cart': True,
    'shipping_address': '123 Test St'
})
order_id = order_response.json()['order_id']

# 2. Process payment
payment_response = requests.post('/api/v1/payments/charge/', {
    'order_id': order_id,
    'payment_method': 'credit_card',
    'card_number': '4111111111111111',
    'card_holder': 'Test User',
    'card_expiry': '12/2025',
    'card_cvv': '123'
})

# 3. Check result
if payment_response.json()['status'] == 'completed':
    print("Payment successful!")
else:
    print(f"Payment failed: {payment_response.json()['message']}")
```

## Troubleshooting

### Common Issues

1. **Authentication Required Error**
   - Ensure you're logged in (JWT token or session)
   - Check Authorization header format: `Bearer <token>`

2. **Order Not Found** 
   - Verify order exists and belongs to authenticated user
   - Check order status is payable (`pending` or `confirmed`)

3. **Payment Already Processed**
   - Each order can only have one successful payment
   - Check existing payments before retrying

4. **Invalid Card Number**
   - Use provided test card numbers
   - Ensure card number format is correct (digits only)

### Debug Mode

Enable detailed logging by setting:
```env
PAYMENT_LOG_REQUESTS=1
PAYMENT_SIMULATE_DELAYS=1
```

This will log all payment requests and simulate realistic processing delays.

## Production Deployment

When deploying to production:

1. Set `PAYMENT_SANDBOX_MODE=0` in environment
2. Update `PAYMENT_API_KEY` with real gateway credentials  
3. Configure production webhook endpoints
4. Update `PAYMENT_PRODUCTION_URL` setting
5. Test with small amounts before full deployment

## Support

For sandbox issues or questions:
- Check Django logs for detailed error messages
- Use `/api/v1/payments/sandbox/info/` to verify configuration
- Test with provided test card numbers first
- Ensure proper authentication is in place

The sandbox provides a comprehensive testing environment that closely mirrors real payment gateway behavior while being completely safe for development and testing.
