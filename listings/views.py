from django.db import IntegrityError
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import ListingSubmission, Property, Review, ReviewHelpfulVote
from .serializers import (
    AdminReviewSerializer,
    AdminReviewUpdateSerializer,
    ListingSubmissionCreateSerializer,
    ListingSubmissionSerializer,
    PropertySerializer,
    ReviewCreateSerializer,
    ReviewSerializer,
)
from .utils import haversine_km, track_property_view


class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class PropertyNearbyView(APIView):
    """GET /listings/nearby/?lat=&lng=&radius_km= — koordinata atrofidagi e'lonlar."""

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            lat = float(request.query_params.get("lat", ""))
            lng = float(request.query_params.get("lng", ""))
        except (TypeError, ValueError):
            return Response(
                {"detail": "lat va lng majburiy va raqam bo'lishi kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lng <= 180.0):
            return Response(
                {"detail": "Noto'g'ri koordinatalar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            radius = float(request.query_params.get("radius_km", "15"))
        except (TypeError, ValueError):
            radius = 15.0
        radius = max(0.5, min(radius, 100.0))

        qs = (
            Property.objects.prefetch_related("photos")
            .exclude(latitude__isnull=True)
            .exclude(longitude__isnull=True)
        )
        scored: list[tuple[float, Property]] = []
        for p in qs.iterator(chunk_size=200):
            d = haversine_km(lat, lng, float(p.latitude), float(p.longitude))
            if d <= radius:
                scored.append((d, p))
        scored.sort(key=lambda x: x[0])
        scored = scored[:100]
        distances = {str(p.pk): d for d, p in scored}
        items = [p for _, p in scored]
        ser = PropertySerializer(
            items,
            many=True,
            context={"request": request, "distances": distances},
        )
        return Response(ser.data)


class PropertyListView(generics.ListAPIView):
    serializer_class = PropertySerializer
    pagination_class = None

    def get_queryset(self):
        qs = Property.objects.prefetch_related("photos").all()
        category = self.request.query_params.get("category")
        vip_only = self.request.query_params.get("vip")
        if category:
            qs = qs.filter(category_id=category)
        if vip_only and vip_only.lower() in ("1", "true", "yes"):
            qs = qs.filter(vip=True)
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(district__icontains=q))
        return qs


class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.prefetch_related("photos").all()
    serializer_class = PropertySerializer
    lookup_field = "pk"

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["with_my_review"] = True
        return ctx

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        track_property_view(request, instance)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ReviewListCreateView(generics.ListCreateAPIView):
    """GET /listings/{id}/reviews/ — POST sharh (faqat login)."""

    pagination_class = ReviewPagination

    def get_queryset(self):
        pk = self.kwargs["pk"]
        return (
            Review.objects.filter(listing_id=pk)
            .select_related("user")
            .order_by("-is_pinned", "-helpful_count", "-created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_throttles(self):
        if self.request.method == "POST":
            return [ScopedRateThrottle()]
        return super().get_throttles()

    throttle_scope = "review_create"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = get_object_or_404(Property, pk=self.kwargs["pk"])
        try:
            serializer.save(user=request.user, listing=listing)
        except IntegrityError:
            # Bir e'londa bitta baho saqlanadi, ammo foydalanuvchi izohini
            # istalgancha yangilashi mumkin.
            instance = get_object_or_404(
                Review, listing_id=listing.pk, user_id=request.user.id
            )
            comment = serializer.validated_data.get("comment", "")
            if comment:
                instance.comment = comment
                instance.save(update_fields=["comment", "updated_at"])
            return Response(
                ReviewSerializer(instance, context={"request": request}).data,
                status=status.HTTP_200_OK,
            )
        instance = serializer.instance
        return Response(
            ReviewSerializer(instance, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ReviewHelpfulView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "review_helpful"

    def post(self, request, pk, review_id):
        listing = get_object_or_404(Property, pk=pk)
        review = get_object_or_404(Review, pk=review_id, listing=listing)
        vote, created = ReviewHelpfulVote.objects.get_or_create(
            review=review, user=request.user
        )
        if created:
            Review.objects.filter(pk=review.pk).update(helpful_count=F("helpful_count") + 1)
        review.refresh_from_db()
        return Response(
            {
                "helpfulCount": review.helpful_count,
                "isHelpful": True,
            }
        )


class AdminReviewListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminReviewSerializer
    pagination_class = ReviewPagination

    def get_queryset(self):
        qs = Review.objects.select_related("listing", "user").order_by("-created_at")
        lid = self.request.query_params.get("listing")
        if lid:
            qs = qs.filter(listing_id=lid)
        return qs


class AdminReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Review.objects.select_related("listing", "user")
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return AdminReviewSerializer
        return AdminReviewUpdateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = AdminReviewUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.refresh_from_db()
        return Response(
            AdminReviewSerializer(instance, context={"request": request}).data
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class ListingSubmissionCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListingSubmissionCreateSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "submission_create"


class MyListingSubmissionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListingSubmissionSerializer
    pagination_class = None

    def get_queryset(self):
        return ListingSubmission.objects.filter(user=self.request.user).prefetch_related("images")
