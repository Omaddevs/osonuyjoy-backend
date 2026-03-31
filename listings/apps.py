from django.apps import AppConfig


class ListingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "listings"
    verbose_name = "E'lonlar"

    def ready(self) -> None:
        import listings.signals  # noqa: F401, I001
