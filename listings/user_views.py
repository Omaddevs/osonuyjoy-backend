"""Profil va sevimli e'lonlar."""

from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Property, UserFavorite, UserNotification, UserProfile
from .serializers import (
    PropertySerializer,
    UserMeSerializer,
    UserNotificationSerializer,
    UserProfileUpdateSerializer,
)


class UserProfileUpdateView(APIView):
    """PUT /user/profile/ — username va avatar."""

    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def put(self, request):
        ser = UserProfileUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        user = request.user
        if "username" in ser.validated_data:
            username = ser.validated_data["username"]
            if username != user.username:
                if User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
                    return Response(
                        {"detail": "Bu foydalanuvchi nomi band."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user.username = username
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        clear_flag = ser.validated_data.get("clear_avatar") or request.data.get("clear_avatar")
        if clear_flag is True or str(clear_flag).lower() in ("true", "1", "yes"):
            if profile.avatar:
                profile.avatar.delete(save=False)
            profile.avatar = None
        elif "avatar" in ser.validated_data and ser.validated_data.get("avatar") is not None:
            profile.avatar = ser.validated_data["avatar"]
        profile.save()

        # request.user ichidagi listing_profile keshi eski rasmni ushlab qolmasin
        fresh_user = User.objects.select_related("listing_profile").get(pk=user.pk)
        return Response(UserMeSerializer(fresh_user, context={"request": request}).data)


class UserFavoritesListView(APIView):
    """GET /user/favorites/ — saqlangan e'lonlar (oxirgi qo'shilgan birinchi)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        favs = (
            UserFavorite.objects.filter(user=request.user)
            .order_by("-created_at")
            .select_related("listing")
            .prefetch_related("listing__photos")
        )
        listings = [f.listing for f in favs]
        ser = PropertySerializer(
            listings, many=True, context={"request": request}
        )
        return Response(ser.data)


class ListingFavoriteView(APIView):
    """POST/DELETE /listings/<id>/like/"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk: str):
        get_object_or_404(Property, pk=pk)
        UserFavorite.objects.get_or_create(user=request.user, listing_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk: str):
        UserFavorite.objects.filter(user=request.user, listing_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserNotificationsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            UserNotification.objects.filter(user=request.user)
            .select_related("notification")
            .order_by("-notification__created_at")
        )
        return Response(UserNotificationSerializer(qs, many=True).data)


class UserNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        nid = request.data.get("id")
        if nid in (None, ""):
            UserNotification.objects.filter(user=request.user, is_read=False).update(
                is_read=True, read_at=timezone.now()
            )
            return Response({"ok": True})
        row = get_object_or_404(UserNotification, user=request.user, notification_id=nid)
        if not row.is_read:
            row.is_read = True
            row.read_at = timezone.now()
            row.save(update_fields=["is_read", "read_at"])
        return Response({"ok": True})
