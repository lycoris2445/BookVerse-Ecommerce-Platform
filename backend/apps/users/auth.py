from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from apps.users.services.jwt_utils import decode_jwt_token
from apps.users.models import Customer


class CustomerPrincipal:
    def __init__(self, customer_id, email=None):
        self.id = int(customer_id)
        self.email = email
        self.is_authenticated = True

    def __str__(self):
        return f"CustomerPrincipal({self.id})"


class JWTAuthentication(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth.startswith(self.keyword):
            return None
        token = auth.split(' ', 1)[1]
        try:
            payload = decode_jwt_token(token)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid or expired token')

        if not payload:
            raise exceptions.AuthenticationFailed('Invalid or expired token')

        cid = payload.get('sub')
        if cid is None:
            raise exceptions.AuthenticationFailed('Invalid token payload')

        try:
            cid = int(cid)  # Convert string subject back to integer
        except (ValueError, TypeError):
            raise exceptions.AuthenticationFailed('Invalid customer ID in token')

        try:
            cust = Customer.objects.get(CustomerID=cid)
        except Customer.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

        principal = CustomerPrincipal(customer_id=cid, email=payload.get('email'))
        return (principal, token)


class SessionCustomerAuthentication(BaseAuthentication):
    """Authenticate using request.session['customer_id'].

    If a valid customer_id exists in the session, return a CustomerPrincipal.
    Otherwise return None to allow other authentication classes to run.
    """

    def authenticate(self, request):
        cid = request.session.get('customer_id')
        if not cid:
            return None

        try:
            # Keep lookup lightweight; only ensure the referenced customer exists
            cust = Customer.objects.get(CustomerID=cid)
        except Customer.DoesNotExist:
            # If session contains an invalid id, treat as unauthenticated
            return None

        principal = CustomerPrincipal(customer_id=cid, email=getattr(cust, 'Email', None))
        return (principal, None)
