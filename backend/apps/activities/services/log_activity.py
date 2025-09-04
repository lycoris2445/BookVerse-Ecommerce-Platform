from django.utils import timezone
from ..models import UserActivity
from typing import Optional

def log_event(*, customer_id: Optional[int], book_id: int, action: str, session_id: Optional[str], when=None) -> UserActivity:
    if customer_id is None:
        raise ValueError("Login required to log activity")
    ua = UserActivity(
        CustomerID=customer_id,
        BookID=book_id,
        Action=action,
        ActivityTime=when or timezone.now(),
        SessionID=session_id,
    )
    # force_insert ensures an INSERT is executed (no migrations/manipulation of schema)
    ua.save(force_insert=True)
    return ua
