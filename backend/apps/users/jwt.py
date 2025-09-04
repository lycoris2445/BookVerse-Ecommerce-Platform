import jwt
import uuid
from datetime import datetime, timedelta, timezone
from django.conf import settings


def now_utc():
    return datetime.now(timezone.utc)


def _secret():
    return getattr(settings, 'JWT_SECRET', getattr(settings, 'SECRET_KEY'))


def encode(payload: dict, ttl: timedelta) -> str:
    data = payload.copy()
    iat = now_utc()
    exp = iat + ttl
    data.update({
        'iat': int(iat.timestamp()),
        'exp': int(exp.timestamp()),
        'jti': data.get('jti') or uuid.uuid4().hex,
    })
    token = jwt.encode(data, _secret(), algorithm='HS256')
    return token


def decode(token: str) -> dict:
    try:
        return jwt.decode(token, _secret(), algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise
    except Exception:
        raise


def issue_tokens(customer, access_minutes=None, refresh_days=None):
    access_minutes = access_minutes or int(getattr(settings, 'JWT_ACCESS_TTL_MINUTES', 15))
    refresh_days = refresh_days or int(getattr(settings, 'JWT_REFRESH_TTL_DAYS', 7))

    access_ttl = timedelta(minutes=int(access_minutes))
    refresh_ttl = timedelta(days=int(refresh_days))

    now = now_utc()
    base = {
        'sub': int(customer.CustomerID),
        'email': getattr(customer, 'Email', ''),
    }

    access_payload = {**base, 'type': 'access'}
    refresh_payload = {**base, 'type': 'refresh'}

    access = encode(access_payload, access_ttl)
    refresh = encode(refresh_payload, refresh_ttl)

    access_exp = now + access_ttl

    return {
        'access': access,
        'refresh': refresh,
        'access_expires_at': int(access_exp.timestamp())
    }
