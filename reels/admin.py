from django.contrib import admin

from .models import Reel


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "location", "category", "views", "is_active", "sort_order")
    list_filter = ("category", "is_active")
    search_fields = ("title", "location", "id")
