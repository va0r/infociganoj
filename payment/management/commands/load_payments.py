from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load payment data from fixtures'

    def handle(self, *args, **options):
        call_command('loaddata', 'payments_fixture.json')
