from rest_framework import generics

from .models import Reel
from .serializers import ReelSerializer


class ReelListView(generics.ListAPIView):
    serializer_class = ReelSerializer
    pagination_class = None

    def get_queryset(self):
        qs = Reel.objects.filter(is_active=True)
        category = self.request.query_params.get("category")
        if category and category != "all":
            qs = qs.filter(category=category)
        return qs


class ReelDetailView(generics.RetrieveAPIView):
    queryset = Reel.objects.filter(is_active=True)
    serializer_class = ReelSerializer
    lookup_field = "pk"
