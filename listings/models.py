from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Property(models.Model):
    """Ko'chmas mulk e'loni — frontend `PropertyListing` bilan mos."""

    class Category(models.TextChoices):
        UYLAR = "uylar", "Uylar"
        IJARA = "ijara", "Ijara"
        HOVLI = "hovli", "Hovli"
        KVARTIRA = "kvartira", "Kvartira"
        DACHA = "dacha", "Dacha"
        MEHMONXONA = "mehmonxona", "Mehmonxona"
        QURUQ_YER = "quruq-yer", "Quruq yer"

    id = models.CharField("E'lon ID", max_length=64, primary_key=True)
    title = models.CharField("Sarlavha", max_length=500)
    type_label = models.CharField(
        "Mulk turi (ko'rinadigan matn)",
        max_length=64,
        help_text="Masalan: Kvartira, Hovli.",
    )
    category_id = models.CharField(
        "Kategoriya kodi",
        max_length=32,
        db_index=True,
        choices=Category.choices,
        help_text="Ro'yxatdan tanlang: uylar, ijara, hovli, kvartira, dacha, mehmonxona, quruq-yer.",
    )
    vip = models.BooleanField("VIP e'lon", default=False)
    views_count = models.PositiveIntegerField("Ko'rishlar soni", default=0)
    rating_avg = models.DecimalField(
        "O'rtacha baho (1–5)",
        max_digits=3,
        decimal_places=2,
        default=0,
    )
    rating_count = models.PositiveIntegerField("Baholar / sharhlar soni", default=0)
    district = models.CharField("Tuman / mahalla", max_length=128)
    region = models.CharField("Shahar / viloyat", max_length=128)
    address_line = models.CharField("Manzil (qator)", max_length=500)
    latitude = models.FloatField(
        "Kenglik (xarita)",
        null=True,
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        help_text="Xarita (Leaflet/OSM) uchun. Masalan Toshkent: 41.31",
    )
    longitude = models.FloatField(
        "Uzunlik (xarita)",
        null=True,
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        help_text="Masalan: 69.24",
    )
    price = models.CharField(
        "Narx",
        max_length=64,
        help_text="Masalan: $1 500 yoki kelishilgan.",
    )
    price_label = models.CharField(
        "Narx izohi",
        max_length=64,
        default="/ oyiga",
        help_text="Masalan: / oyiga, / sotuv.",
    )
    more_gallery_count = models.PositiveSmallIntegerField(
        "Galereyada qo'shimcha rasm soni (ko'rsatish)",
        default=0,
    )
    beds = models.PositiveSmallIntegerField("Yotoqxona soni", default=0)
    baths = models.PositiveSmallIntegerField("Sanuzel soni", default=0)
    area_m2 = models.PositiveIntegerField("Maydon (m²)", default=0)
    description = models.TextField("Batafsil tavsif", blank=True)
    agent_name = models.CharField("Agent F.I.Sh.", max_length=128)
    agent_avatar = models.URLField("Agent rasmi (havola)", max_length=500)
    agent_phone = models.CharField("Agent telefoni", max_length=32)
    created_at = models.DateTimeField("Yaratilgan vaqt", auto_now_add=True)
    updated_at = models.DateTimeField("Oxirgi o'zgarish", auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"

    def __str__(self) -> str:
        return f"{self.title} ({self.id})"


class PropertyImage(models.Model):
    """E'lon rasmlari — admin orqali cheksiz qo'shish mumkin."""

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="photos",
        related_query_name="photo",
        verbose_name="E'lon",
    )
    image = models.ImageField(
        "Rasm fayli",
        upload_to="listings/%Y/%m/",
        help_text="Bir nechta rasm uchun har bir qatorga alohida rasm tanlang. "
        "Pastdagi tugma orqali qator qo'shishingiz mumkin (cheksiz).",
    )
    sort_order = models.PositiveIntegerField(
        "Tartib raqami",
        default=0,
        help_text="0 — birinchi rasm, keyingi raqamlar keyin chiqadi.",
    )
    created_at = models.DateTimeField("Yuklangan vaqt", auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "E'lon rasmi"
        verbose_name_plural = "E'lon rasmlari"

    def __str__(self) -> str:
        return f"{self.property_id} — {self.image.name}"


class ListingViewDaily(models.Model):
    """Har bir foydalanuvchi / IP uchun kuniga bitta ko'rish yozuvi."""

    listing = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="view_days",
        verbose_name="E'lon",
    )
    date = models.DateField("Sana", db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Foydalanuvchi",
    )
    ip_hash = models.CharField("IP (hash)", max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kunlik ko'rish yozuvi"
        verbose_name_plural = "Kunlik ko'rish yozuvlari"
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "user", "date"],
                condition=Q(user__isnull=False),
                name="listing_view_user_date_uniq",
            ),
            models.UniqueConstraint(
                fields=["listing", "date", "ip_hash"],
                condition=Q(user__isnull=True),
                name="listing_view_ip_date_uniq",
            ),
        ]

    def __str__(self) -> str:
        who = self.user_id or f"ip:{self.ip_hash[:8]}…"
        return f"{self.listing_id} @ {self.date} ({who})"


class Review(models.Model):
    """Bir foydalanuvchi bir e'longa bitta baho + ixtiyoriy sharh."""

    listing = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="E'lon",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listing_reviews",
        verbose_name="Foydalanuvchi",
    )
    rating = models.PositiveSmallIntegerField(
        "Baho",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("Sharh", blank=True)
    helpful_count = models.PositiveIntegerField("Foydali ovozlar", default=0)
    is_pinned = models.BooleanField("Tepada ko'rsatish", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sharh / baho"
        verbose_name_plural = "Sharhlar va baholar"
        ordering = ["-is_pinned", "-helpful_count", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "user"],
                name="review_one_per_user_per_listing",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.listing_id} — {self.user_id} ({self.rating})"


class ReviewHelpfulVote(models.Model):
    """Har bir foydalanuvchi sharhga bir marta «foydali»."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="helpful_votes",
        verbose_name="Sharh",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="helpful_votes",
        verbose_name="Foydalanuvchi",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foydali ovoz"
        verbose_name_plural = "Foydali ovozlar"
        constraints = [
            models.UniqueConstraint(
                fields=["review", "user"],
                name="review_helpful_one_per_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.review_id} + {self.user_id}"


class UserProfile(models.Model):
    """Foydalanuvchi profil rasmi (User bilan 1:1)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listing_profile",
        verbose_name="Foydalanuvchi",
    )
    avatar = models.ImageField(
        "Profil rasmi",
        upload_to="avatars/%Y/%m/",
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Foydalanuvchi profili"
        verbose_name_plural = "Foydalanuvchi profillari"

    def __str__(self) -> str:
        return f"Profil: {self.user_id}"


class UserFavorite(models.Model):
    """Foydalanuvchi saqlagan e'lonlar."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listing_favorites",
        verbose_name="Foydalanuvchi",
    )
    listing = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="user_favorites",
        verbose_name="E'lon",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sevimli e'lon"
        verbose_name_plural = "Sevimli e'lonlar"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "listing"],
                name="user_favorite_listing_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} → {self.listing_id}"


class ListingSubmission(models.Model):
    class Tariff(models.TextChoices):
        SIMPLE = "simple", "Oddiy (50 000 so'm)"
        VIP = "vip", "VIP (250 000 so'm)"

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        APPROVED = "approved", "Tasdiqlandi"
        REJECTED = "rejected", "Rad etildi"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listing_submissions",
    )
    tariff = models.CharField(max_length=12, choices=Tariff.choices, default=Tariff.SIMPLE)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)

    title = models.CharField(max_length=500)
    type_label = models.CharField(max_length=64)
    category_id = models.CharField(max_length=32, choices=Property.Category.choices)
    audience = models.CharField(max_length=64, blank=True, default="")
    district = models.CharField(max_length=128)
    region = models.CharField(max_length=128, default="Toshkent shahri")
    address_line = models.CharField(max_length=500)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    price = models.CharField(max_length=64)
    price_label = models.CharField(max_length=64, default="/ oyiga")
    beds = models.PositiveSmallIntegerField(default=0)
    baths = models.PositiveSmallIntegerField(default=0)
    area_m2 = models.PositiveIntegerField(default=0)
    building_floors = models.PositiveSmallIntegerField(null=True, blank=True)
    floor_number = models.PositiveSmallIntegerField(null=True, blank=True)
    property_condition = models.CharField(max_length=64, blank=True, default="")
    amenities = models.TextField(blank=True, default="")
    extra_info = models.TextField(blank=True, default="")
    description = models.TextField(blank=True)
    phone1 = models.CharField(max_length=32, blank=True, default="")
    phone2 = models.CharField(max_length=32, blank=True, default="")
    phone3 = models.CharField(max_length=32, blank=True, default="")
    payment_card = models.CharField(max_length=64, default="8600 1234 5678 9012")
    payment_proof = models.FileField(upload_to="payment-proofs/%Y/%m/")
    admin_note = models.TextField(blank=True, default="")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "To'lovli e'lon arizasi"
        verbose_name_plural = "To'lovli e'lon arizalari"

    def __str__(self) -> str:
        return f"{self.title} ({self.user_id}) [{self.status}]"

    def approve_to_property(self) -> Property:
        prop = Property.objects.create(
            id=f"u{self.pk}",
            title=self.title,
            type_label=self.type_label,
            category_id=self.category_id,
            vip=self.tariff == self.Tariff.VIP,
            district=self.district,
            region=self.region,
            address_line=self.address_line,
            latitude=self.latitude,
            longitude=self.longitude,
            price=self.price,
            price_label=self.price_label,
            beds=self.beds,
            baths=self.baths,
            area_m2=self.area_m2,
            description=self.description,
            more_gallery_count=max(self.images.count() - 1, 0),
            agent_name=self.user.get_full_name().strip() or self.user.username,
            agent_avatar="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=200&q=80&auto=format&fit=crop",
            agent_phone=self.phone1 or self.phone2 or self.phone3 or "+998 90 000 00 00",
        )
        for i, img in enumerate(self.images.all().order_by("id")):
            if img.image:
                PropertyImage.objects.create(property=prop, image=img.image, sort_order=i)
        self.status = self.Status.APPROVED
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_at", "updated_at"])
        return prop


class ListingSubmissionImage(models.Model):
    submission = models.ForeignKey(
        ListingSubmission, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="submission-images/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Ariza rasmi"
        verbose_name_plural = "Ariza rasmlari"


class Notification(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_notifications",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"

    def __str__(self) -> str:
        return self.title


class UserNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="recipients",
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "notification"], name="uniq_user_notification"
            )
        ]
        verbose_name = "Foydalanuvchi bildirishnomasi"
        verbose_name_plural = "Foydalanuvchi bildirishnomalari"
