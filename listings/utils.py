"""E'lon ko'rishlari, IP va matn tozalash."""
from __future__ import annotations

import hashlib
from math import asin, cos, radians, sin, sqrt

from django.db.models import F
from django.utils import timezone


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Ikki nuqta orasidagi masofa (km)."""
    r = 6371.0
    p1, q1, p2, q2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat = p2 - p1
    dlon = q2 - q1
    a = sin(dlat / 2) ** 2 + cos(p1) * cos(p2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(min(1.0, a)))
    return r * c


def get_client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or ""


def track_property_view(request, property_obj) -> None:
    """Kuniga 1 marta: autentifikatsiyalangan — user bo'yicha; anonim — IP hash bo'yicha."""
    from .models import ListingViewDaily, Property

    today = timezone.localdate()

    if request.user.is_authenticated:
        exists = ListingViewDaily.objects.filter(
            listing=property_obj, user=request.user, date=today
        ).exists()
        if not exists:
            ListingViewDaily.objects.create(
                listing=property_obj, user=request.user, date=today, ip_hash=""
            )
            Property.objects.filter(pk=property_obj.pk).update(views_count=F("views_count") + 1)
        return

    ip = get_client_ip(request)
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:32]
    exists = ListingViewDaily.objects.filter(
        listing=property_obj, user__isnull=True, date=today, ip_hash=ip_hash
    ).exists()
    if not exists:
        ListingViewDaily.objects.create(
            listing=property_obj, user=None, date=today, ip_hash=ip_hash
        )
        Property.objects.filter(pk=property_obj.pk).update(views_count=F("views_count") + 1)


def sanitize_comment(text: str) -> str:
    """HTML/XSS uchun cheklangan teglar; qolgani olib tashlanadi."""
    if not text or not str(text).strip():
        return ""
    try:
        import bleach
    except ImportError:
        return str(text).strip()[:5000]
    allowed = {"b", "i", "strong", "em", "br", "p"}
    return bleach.clean(str(text).strip(), tags=allowed, strip=True)[:5000]
