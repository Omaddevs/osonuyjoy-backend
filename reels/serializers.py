from rest_framework import serializers

from .models import Reel


class ReelSerializer(serializers.ModelSerializer):
    """Frontend `Reel` tipi bilan mos (video_url, title, location, category, views)."""

    class Meta:
        model = Reel
        fields = ["id", "video_url", "title", "location", "category", "views"]
