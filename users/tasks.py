from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task
def disconnect_inactive_users():
    expire_date = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(last_login__lte=expire_date)
    inactive_users.update(is_active=False)
