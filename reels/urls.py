from django.urls import path

from . import views

urlpatterns = [
    path("", views.ReelListView.as_view(), name="reel-list"),
    path("<str:pk>/", views.ReelDetailView.as_view(), name="reel-detail"),
]
