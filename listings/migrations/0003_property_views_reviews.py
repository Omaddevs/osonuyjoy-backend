# Generated manually — views, rating maydonlari, sharhlar.

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


def copy_rating_fields(apps, schema_editor):
    Property = apps.get_model("listings", "Property")
    for p in Property.objects.all():
        rc = p.review_count
        rt = p.rating or "0"
        try:
            avg = float(str(rt).replace(",", "."))
        except (ValueError, TypeError):
            avg = 0.0
        Property.objects.filter(pk=p.pk).update(
            rating_count=rc,
            rating_avg=Decimal(str(round(avg, 2))),
            views_count=0,
        )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("listings", "0002_property_images"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="views_count",
            field=models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar soni"),
        ),
        migrations.AddField(
            model_name="property",
            name="rating_avg",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=3,
                verbose_name="O'rtacha baho (1–5)",
            ),
        ),
        migrations.AddField(
            model_name="property",
            name="rating_count",
            field=models.PositiveIntegerField(default=0, verbose_name="Baholar / sharhlar soni"),
        ),
        migrations.RunPython(copy_rating_fields, migrations.RunPython.noop),
        migrations.RemoveField(model_name="property", name="rating"),
        migrations.RemoveField(model_name="property", name="review_count"),
        migrations.CreateModel(
            name="ListingViewDaily",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(db_index=True, verbose_name="Sana")),
                ("ip_hash", models.CharField(blank=True, default="", max_length=64, verbose_name="IP (hash)")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="view_days",
                        to="listings.property",
                        verbose_name="E'lon",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Foydalanuvchi",
                    ),
                ),
            ],
            options={
                "verbose_name": "Kunlik ko'rish yozuvi",
                "verbose_name_plural": "Kunlik ko'rish yozuvlari",
            },
        ),
        migrations.AddConstraint(
            model_name="listingviewdaily",
            constraint=models.UniqueConstraint(
                condition=Q(user__isnull=False),
                fields=("listing", "user", "date"),
                name="listing_view_user_date_uniq",
            ),
        ),
        migrations.AddConstraint(
            model_name="listingviewdaily",
            constraint=models.UniqueConstraint(
                condition=Q(user__isnull=True),
                fields=("listing", "date", "ip_hash"),
                name="listing_view_ip_date_uniq",
            ),
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name="Baho")),
                ("comment", models.TextField(blank=True, verbose_name="Sharh")),
                ("helpful_count", models.PositiveIntegerField(default=0, verbose_name="Foydali ovozlar")),
                ("is_pinned", models.BooleanField(default=False, verbose_name="Tepada ko'rsatish")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="listings.property",
                        verbose_name="E'lon",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="listing_reviews",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Foydalanuvchi",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sharh / baho",
                "verbose_name_plural": "Sharhlar va baholar",
                "ordering": ("-is_pinned", "-helpful_count", "-created_at"),
            },
        ),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.UniqueConstraint(fields=("listing", "user"), name="review_one_per_user_per_listing"),
        ),
        migrations.CreateModel(
            name="ReviewHelpfulVote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "review",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="helpful_votes",
                        to="listings.review",
                        verbose_name="Sharh",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="helpful_votes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Foydalanuvchi",
                    ),
                ),
            ],
            options={
                "verbose_name": "Foydali ovoz",
                "verbose_name_plural": "Foydali ovozlar",
            },
        ),
        migrations.AddConstraint(
            model_name="reviewhelpfulvote",
            constraint=models.UniqueConstraint(fields=("review", "user"), name="review_helpful_one_per_user"),
        ),
    ]
