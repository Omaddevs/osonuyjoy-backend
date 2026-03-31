from django.urls import path

from . import views
from .user_views import ListingFavoriteView

urlpatterns = [
    path("submissions/", views.ListingSubmissionCreateView.as_view(), name="listing-submission-create"),
    path("submissions/mine/", views.MyListingSubmissionListView.as_view(), name="listing-submission-mine"),
    path("nearby/", views.PropertyNearbyView.as_view(), name="property-nearby"),
    path("", views.PropertyListView.as_view(), name="property-list"),
    path(
        "<str:pk>/reviews/<int:review_id>/helpful/",
        views.ReviewHelpfulView.as_view(),
        name="review-helpful",
    ),
    path("<str:pk>/reviews/", views.ReviewListCreateView.as_view(), name="listing-reviews"),
    path("<str:pk>/like/", ListingFavoriteView.as_view(), name="listing-like"),
    path("<str:pk>/", views.PropertyDetailView.as_view(), name="property-detail"),
]
