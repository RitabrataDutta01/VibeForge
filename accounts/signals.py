from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if not created:
        return
    if hasattr(instance, "profile"):
        return
    Profile.objects.create(
        user=instance,
        role="ADMIN" if instance.is_superuser else "EMPLOYEE",
        employee_id=f"EMP{instance.pk:04d}",
    )