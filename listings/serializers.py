from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    ListingSubmission,
    ListingSubmissionImage,
    Property,
    Review,
    UserNotification,
    UserProfile,
)
from .utils import sanitize_comment


class PropertySerializer(serializers.ModelSerializer):
    """Frontend `PropertyListing` (camelCase) formatiga mos."""

    type = serializers.CharField(source="type_label")
    categoryId = serializers.CharField(source="category_id")
    reviewCount = serializers.IntegerField(source="rating_count")
    viewsCount = serializers.IntegerField(source="views_count", read_only=True)
    priceLabel = serializers.CharField(source="price_label")
    moreGalleryCount = serializers.IntegerField(source="more_gallery_count")
    areaM2 = serializers.IntegerField(source="area_m2")
    addressLine = serializers.CharField(source="address_line")
    rating = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    myReview = serializers.SerializerMethodField()
    latitude = serializers.FloatField(allow_null=True, required=False)
    longitude = serializers.FloatField(allow_null=True, required=False)
    distanceKm = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "type",
            "categoryId",
            "vip",
            "rating",
            "reviewCount",
            "viewsCount",
            "district",
            "region",
            "addressLine",
            "latitude",
            "longitude",
            "distanceKm",
            "price",
            "priceLabel",
            "images",
            "moreGalleryCount",
            "beds",
            "baths",
            "areaM2",
            "description",
            "agent",
            "myReview",
        ]

    def get_rating(self, obj: Property) -> str:
        if obj.rating_count == 0:
            return "0"
        avg = obj.rating_avg
        if avg is None:
            return "0"
        return f"{float(avg):.1f}"

    def get_agent(self, obj: Property) -> dict:
        return {
            "name": obj.agent_name,
            "avatar": obj.agent_avatar,
            "phone": obj.agent_phone,
        }

    def get_images(self, obj: Property) -> list[str]:
        request = self.context.get("request")
        urls: list[str] = []
        for photo in obj.photos.all():
            if not photo.image:
                continue
            url = photo.image.url
            if request is not None:
                url = request.build_absolute_uri(url)
            urls.append(url)
        return urls

    def get_distanceKm(self, obj: Property) -> float | None:
        raw = self.context.get("distances", {}).get(str(obj.pk))
        if raw is None:
            return None
        return round(float(raw), 3)

    def get_myReview(self, obj: Property) -> dict | None:
        """Faqat detail sahifada (with_my_review) va login bo'lsa — foydalanuvchi bahosi."""
        if not self.context.get("with_my_review"):
            return None
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        rev = (
            Review.objects.filter(listing_id=obj.pk, user_id=request.user.id)
            .only("id", "rating")
            .first()
        )
        if not rev:
            return None
        return {"id": rev.id, "rating": rev.rating}


class ReviewSerializer(serializers.ModelSerializer):
    """Sharhlar ro'yxati — o'qish uchun."""

    userId = serializers.IntegerField(source="user_id", read_only=True)
    userName = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    helpfulCount = serializers.IntegerField(source="helpful_count", read_only=True)
    isHelpful = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()
    isPinned = serializers.BooleanField(source="is_pinned", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "userId",
            "userName",
            "rating",
            "comment",
            "createdAt",
            "helpfulCount",
            "isHelpful",
            "verified",
            "isPinned",
        ]

    def get_userName(self, obj: Review) -> str:
        u = obj.user
        if u.get_full_name().strip():
            return u.get_full_name().strip()
        return u.username

    def get_isHelpful(self, obj: Review) -> bool:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.helpful_votes.filter(user_id=request.user.id).exists()

    def get_verified(self, obj: Review) -> bool:
        return bool(obj.user.is_staff)


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("rating", "comment")

    def validate_rating(self, value: int) -> int:
        if value < 1 or value > 5:
            raise serializers.ValidationError("Baho 1 dan 5 gacha bo'lishi kerak.")
        return value

    def validate_comment(self, value: str) -> str:
        return sanitize_comment(value or "")


class AdminReviewUpdateSerializer(serializers.ModelSerializer):
    """Admin moderatsiya — matn va bahoni tahrirlash."""

    class Meta:
        model = Review
        fields = ("rating", "comment", "is_pinned")

    def validate_rating(self, value: int) -> int:
        if value < 1 or value > 5:
            raise serializers.ValidationError("Baho 1 dan 5 gacha bo'lishi kerak.")
        return value

    def validate_comment(self, value: str) -> str:
        return sanitize_comment(value or "")


class AdminReviewSerializer(serializers.ModelSerializer):
    """Admin panel — e'lon va foydalanuvchi bilan."""

    listingId = serializers.CharField(source="listing_id", read_only=True)
    listingTitle = serializers.CharField(source="listing.title", read_only=True)
    userId = serializers.IntegerField(source="user_id", read_only=True)
    userName = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "listingId",
            "listingTitle",
            "userId",
            "userName",
            "rating",
            "comment",
            "createdAt",
            "helpful_count",
            "is_pinned",
        ]

    def get_userName(self, obj: Review) -> str:
        u = obj.user
        if u.get_full_name().strip():
            return u.get_full_name().strip()
        return u.username


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Bu foydalanuvchi nomi band.")
        return value

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Bu email band.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Parollar mos emas."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        UserProfile.objects.get_or_create(user=user)
        return user


class UserMeSerializer(serializers.ModelSerializer):
    """GET /auth/me / profil uchun."""

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "avatar")

    def get_avatar(self, obj: User) -> str | None:
        """Profil rasmi — to'liq URL."""
        try:
            prof = obj.listing_profile
        except UserProfile.DoesNotExist:
            return None
        if not prof.avatar:
            return None
        request = self.context.get("request")
        url = prof.avatar.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class UserProfileUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    avatar = serializers.ImageField(required=False, allow_null=True)
    clear_avatar = serializers.BooleanField(required=False, default=False)

    def validate_username(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("Foydalanuvchi nomi bo'sh bo'lmasligi kerak.")
        return value.strip()

    def validate(self, attrs):
        if attrs.get("clear_avatar") and attrs.get("avatar"):
            raise serializers.ValidationError(
                "Rasmni bir vaqtning o'zida o'chirib va yangi yuklab bo'lmaydi."
            )
        return attrs


class ListingSubmissionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingSubmissionImage
        fields = ("id", "image")


class ListingSubmissionSerializer(serializers.ModelSerializer):
    images = ListingSubmissionImageSerializer(many=True, read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    reviewedAt = serializers.DateTimeField(source="reviewed_at", read_only=True)

    class Meta:
        model = ListingSubmission
        fields = (
            "id",
            "tariff",
            "status",
            "title",
            "type_label",
            "category_id",
            "audience",
            "district",
            "region",
            "address_line",
            "latitude",
            "longitude",
            "price",
            "price_label",
            "beds",
            "baths",
            "area_m2",
            "building_floors",
            "floor_number",
            "property_condition",
            "amenities",
            "extra_info",
            "description",
            "phone1",
            "phone2",
            "phone3",
            "payment_card",
            "payment_proof",
            "images",
            "admin_note",
            "createdAt",
            "reviewedAt",
        )


class ListingSubmissionCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), required=False, allow_empty=True
    )

    class Meta:
        model = ListingSubmission
        fields = (
            "tariff",
            "title",
            "type_label",
            "category_id",
            "audience",
            "district",
            "region",
            "address_line",
            "latitude",
            "longitude",
            "price",
            "price_label",
            "beds",
            "baths",
            "area_m2",
            "building_floors",
            "floor_number",
            "property_condition",
            "amenities",
            "extra_info",
            "description",
            "phone1",
            "phone2",
            "phone3",
            "payment_proof",
            "images",
        )

    def validate_images(self, value):
        if not value:
            raise serializers.ValidationError("Kamida 1 ta rasm yuklang.")
        return value

    def validate(self, attrs):
        phones = [attrs.get("phone1", "").strip(), attrs.get("phone2", "").strip(), attrs.get("phone3", "").strip()]
        filled = [p for p in phones if p]
        if len(filled) == 0:
            raise serializers.ValidationError({"phone1": "Kamida 1 ta telefon raqam kiriting."})
        if len(filled) > 3:
            raise serializers.ValidationError({"phone1": "Maksimum 3 ta telefon raqam mumkin."})
        if attrs.get("category_id") == "kvartira":
            if attrs.get("building_floors") is None or attrs.get("floor_number") is None:
                raise serializers.ValidationError(
                    "Kvartira uchun necha qavatli bino va nechanchi qavatda ekanini kiriting."
                )
        return attrs

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        req = self.context["request"]
        sub = ListingSubmission.objects.create(user=req.user, **validated_data)
        for image in images:
            ListingSubmissionImage.objects.create(submission=sub, image=image)
        return sub


class UserNotificationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="notification_id", read_only=True)
    title = serializers.CharField(source="notification.title", read_only=True)
    body = serializers.CharField(source="notification.body", read_only=True)
    at = serializers.DateTimeField(source="notification.created_at", read_only=True)
    read = serializers.BooleanField(source="is_read", read_only=True)

    class Meta:
        model = UserNotification
        fields = ("id", "title", "body", "at", "read")
