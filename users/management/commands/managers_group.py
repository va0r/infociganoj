from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create a group of managers'

    def handle(self, *args, **options):
        try:
            managers_group = Group.objects.get(name='Managers')
            self.stdout.write(self.style.SUCCESS('Managers group already exists.'))
        except Group.DoesNotExist:
            managers_group = Group.objects.create(name='Managers')
            self.stdout.write(self.style.SUCCESS('Managers group created successfully.'))
