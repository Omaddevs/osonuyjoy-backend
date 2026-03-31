from django.db import models


class Reel(models.Model):
    class Category(models.TextChoices):
        UY = "uy", "Uy"
        KVARTIRA = "kvartira", "Kvartira"
        IJARA = "ijara", "Ijara"

    id = models.CharField(max_length=64, primary_key=True)
    video_url = models.URLField(max_length=500)
    title = models.CharField(max_length=500)
    location = models.CharField(max_length=128)
    category = models.CharField(
        max_length=16,
        choices=Category.choices,
        default=Category.UY,
        db_index=True,
    )
    views = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Reel"
        verbose_name_plural = "Reels"

    def __str__(self) -> str:
        return self.title
