import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings

SECRET = getattr(settings, 'SECRET_KEY', 'dev-secret')
ALGORITHM = 'HS256'


def create_jwt_token(customer_id, expires_minutes=60*24*7):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(customer_id),  # JWT subject must be a string
        'iat': now,
        'exp': now + timedelta(minutes=expires_minutes)
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token


def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
    except Exception:
        return None  # Other error
