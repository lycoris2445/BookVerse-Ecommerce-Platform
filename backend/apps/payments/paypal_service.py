"""
PayPal REST API integration service
Handles PayPal payments using official PayPal SDK
"""
import os
import json
import logging
from decimal import Decimal
from typing import Dict, Optional, Any

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


class PayPalService:
    """PayPal REST API service for handling payments"""
    
    def __init__(self):
        # PayPal configuration from environment
        self.mode = os.environ.get('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
        self.client_id = os.environ.get('PAYPAL_CLIENT_ID')
        self.client_secret = os.environ.get('PAYPAL_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("PayPal credentials not configured in environment variables")
        
        # API endpoints
        if self.mode == 'sandbox':
            self.base_url = 'https://api-m.sandbox.paypal.com'
        else:
            self.base_url = 'https://api-m.paypal.com'
            
        self._access_token = None
    
    def _get_access_token(self) -> str:
        """Get OAuth2 access token from PayPal"""
        if self._access_token:
            return self._access_token
            
        url = f"{self.base_url}/v1/oauth2/token"
        
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        
        data = 'grant_type=client_credentials'
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret),
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get('access_token')
            
            logger.info(f"PayPal access token obtained successfully")
            return self._access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get PayPal access token: {e}")
            raise
    
    def create_order(self, amount: Decimal, currency: str = 'USD', order_id: str = None) -> Dict[str, Any]:
        """Create PayPal order"""
        access_token = self._get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'PayPal-Request-Id': f'order-{order_id}' if order_id else None
        }
        
        # Remove None values
        headers = {k: v for k, v in headers.items() if v is not None}
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(order_id) if order_id else "default",
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    }
                }
            ],
            "application_context": {
                "brand_name": "EcomTech Bookstore",
                "landing_page": "NO_PREFERENCE",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW",
                "return_url": f"{settings.FRONTEND_URL}/payment/success",
                "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            order_data = response.json()
            logger.info(f"PayPal order created: {order_data.get('id')}")
            
            return {
                'success': True,
                'order_id': order_data.get('id'),
                'status': order_data.get('status'),
                'links': order_data.get('links', []),
                'raw_response': order_data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create PayPal order: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_response': getattr(e.response, 'json', lambda: {})()
            }
    
    def capture_order(self, paypal_order_id: str) -> Dict[str, Any]:
        """Capture/finalize PayPal order payment"""
        access_token = self._get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders/{paypal_order_id}/capture"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            response = requests.post(url, headers=headers, json={}, timeout=30)
            response.raise_for_status()
            
            capture_data = response.json()
            logger.info(f"PayPal order captured: {paypal_order_id}")
            
            return {
                'success': True,
                'order_id': capture_data.get('id'),
                'status': capture_data.get('status'),
                'payer': capture_data.get('payer', {}),
                'purchase_units': capture_data.get('purchase_units', []),
                'raw_response': capture_data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to capture PayPal order {paypal_order_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_response': getattr(e.response, 'json', lambda: {})()
            }
    
    def get_order_details(self, paypal_order_id: str) -> Dict[str, Any]:
        """Get PayPal order details"""
        access_token = self._get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders/{paypal_order_id}"
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            order_data = response.json()
            
            return {
                'success': True,
                'order_data': order_data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get PayPal order details {paypal_order_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
