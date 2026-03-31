from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model

from .models import (
    ListingSubmission,
    ListingSubmissionImage,
    ListingViewDaily,
    Notification,
    Property,
    PropertyImage,
    Review,
    ReviewHelpfulVote,
    UserNotification,
    UserFavorite,
    UserProfile,
)

admin.site.site_header = "Oson uy-joy — boshqaruv"
admin.site.site_title = "Oson uy-joy"
admin.site.index_title = "Bosh sahifa"


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    min_num = 0
    max_num = None
    fields = ("image", "sort_order")
    ordering = ("sort_order", "id")
    verbose_name = "Rasm"
    verbose_name_plural = (
        "Rasmlar — bir nechta rasm uchun qator qo'shing (cheksiz). "
        "Avval «Saqlash» ni bosing, keyin yana rasm qo'shishingiz mumkin."
    )


class ListingSubmissionImageInline(admin.TabularInline):
    model = ListingSubmissionImage
    extra = 0
    fields = ("image", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category_id",
        "district",
        "vip",
        "views_count",
        "rating_avg",
        "rating_count",
        "price",
    )
    list_filter = ("category_id", "vip")
    search_fields = ("title", "district", "id")
    inlines = (PropertyImageInline,)
    fieldsets = (
        (
            "Asosiy",
            {
                "fields": (
                    "id",
                    "title",
                    "type_label",
                    "category_id",
                    "vip",
                    "views_count",
                    "rating_avg",
                    "rating_count",
                )
            },
        ),
        (
            "Manzil va narx",
            {
                "fields": (
                    "district",
                    "region",
                    "address_line",
                    "latitude",
                    "longitude",
                    "price",
                    "price_label",
                )
            },
        ),
        (
            "Xususiyatlar",
            {
                "fields": (
                    "beds",
                    "baths",
                    "area_m2",
                    "more_gallery_count",
                    "description",
                )
            },
        ),
        (
            "Agent",
            {
                "fields": ("agent_name", "agent_avatar", "agent_phone"),
            },
        ),
        (
            "Texnik",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "sort_order", "created_at")
    list_filter = ("property",)
    search_fields = ("property__title", "property__id")
    list_select_related = ("property",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "listing",
        "user",
        "rating",
        "helpful_count",
        "is_pinned",
        "created_at",
    )
    list_filter = ("listing", "rating", "is_pinned")
    search_fields = ("comment", "listing__title", "user__username")
    autocomplete_fields = ("listing", "user")
    readonly_fields = ("created_at", "updated_at", "helpful_count")


@admin.register(ListingViewDaily)
class ListingViewDailyAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "date", "user", "ip_hash", "created_at")
    list_filter = ("date",)
    search_fields = ("listing__title", "listing__id")


@admin.register(ReviewHelpfulVote)
class ReviewHelpfulVoteAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "user", "created_at")
    autocomplete_fields = ("review", "user")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "updated_at")
    search_fields = ("user__username",)
    autocomplete_fields = ("user",)


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing", "created_at")
    list_filter = ("created_at",)
    search_fields = ("listing__title", "listing__id", "user__username")
    autocomplete_fields = ("user", "listing")


@admin.register(ListingSubmission)
class ListingSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "tariff", "status", "created_at", "reviewed_at")
    list_filter = ("tariff", "status", "category_id", "created_at")
    search_fields = ("title", "district", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "reviewed_at")
    inlines = (ListingSubmissionImageInline,)
    actions = ("approve_and_publish",)

    @admin.action(description="Tanlangan arizalarni tasdiqlab e'lon sifatida joylash")
    def approve_and_publish(self, request, queryset):
        done = 0
        for sub in queryset:
            if sub.status == ListingSubmission.Status.APPROVED:
                continue
            sub.approve_to_property()
            done += 1
        self.message_user(request, f"{done} ta ariza e'longa aylantirildi.")


class NotificationAdminForm(forms.ModelForm):
    send_to_all = forms.BooleanField(required=False, label="Barcha userlarga yuborish")
    recipients = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all().order_by("id"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Tanlangan userlar",
    )

    class Meta:
        model = Notification
        fields = ("title", "body", "send_to_all", "recipients")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm
    list_display = ("id", "title", "created_by", "created_at")
    readonly_fields = ("created_by", "created_at")
    search_fields = ("title", "body")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        recipients = form.cleaned_data.get("recipients")
        send_to_all = form.cleaned_data.get("send_to_all")
        User = get_user_model()
        users = User.objects.all() if send_to_all else recipients
        if users:
            rows = [
                UserNotification(user=u, notification=obj)
                for u in users
            ]
            UserNotification.objects.bulk_create(rows, ignore_conflicts=True)


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "notification", "is_read", "created_at", "read_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "user__email", "notification__title")
    autocomplete_fields = ("user", "notification")
