from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='admin@admin.admin',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

        user.set_password('a8cGZYun5F5KusRJ')
        user.save()
