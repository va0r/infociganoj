from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='mod@mod.mod',
            is_staff=False,
            is_superuser=False,
            is_active=True,
        )

        user.set_password('a8cGZYun5F5KusRJ')
        user.save()
