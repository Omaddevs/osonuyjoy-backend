import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create/update admin user from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "").strip()
        password = os.environ.get("ADMIN_PASSWORD", "").strip()
        email = os.environ.get("ADMIN_EMAIL", "admin@example.com").strip()

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "ADMIN_USERNAME yoki ADMIN_PASSWORD topilmadi. Admin yaratilmadi."
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        state = "yaratildi" if created else "yangilandi"
        self.stdout.write(self.style.SUCCESS(f"Admin {state}: {username}"))
