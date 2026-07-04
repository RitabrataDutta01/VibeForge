from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Profile


class Command(BaseCommand):
    help = "Create a Profile for any existing User that doesn't already have one."

    def handle(self, *args, **options):
        created_count = 0
        for user in User.objects.all():
            if hasattr(user, "profile"):
                continue
            Profile.objects.create(
                user=user,
                role="ADMIN" if user.is_superuser else "EMPLOYEE",
                employee_id=f"EMP{user.pk:04d}",
            )
            created_count += 1
            self.stdout.write(f"Created profile for '{user.username}' ({'ADMIN' if user.is_superuser else 'EMPLOYEE'})")

        if created_count == 0:
            self.stdout.write(self.style.SUCCESS("All users already have profiles."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Backfilled {created_count} profile(s)."))