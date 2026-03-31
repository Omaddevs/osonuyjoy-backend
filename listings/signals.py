from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Property, Review


def refresh_listing_rating(listing_id: str) -> None:
    agg = Review.objects.filter(listing_id=listing_id).aggregate(
        avg=Avg("rating"), c=Count("id")
    )
    avg = agg["avg"]
    if avg is None:
        avg = 0
    Property.objects.filter(pk=listing_id).update(
        rating_avg=avg,
        rating_count=agg["c"] or 0,
    )


@receiver([post_save, post_delete], sender=Review)
def update_listing_rating_on_review_change(sender, instance: Review, **kwargs) -> None:
    refresh_listing_rating(instance.listing_id)
