import logging

from django.core.management.base import BaseCommand

from export_lsd.models import Formato931
from export_lsd.tables.tabla_init_data import TABLA_FORMATO931

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize Formato931 table with default data'

    def handle(self, *args, **options):
        for item in TABLA_FORMATO931:
            obj, created = Formato931.objects.get_or_create(
                id=item['id'],
                defaults={
                    'name': item['name'],
                    'fromm': item['fromm'],
                    'long': item['long'],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Formato931 "{obj.name}" created'))
            else:
                updated = False
                if obj.name != item['name']:
                    obj.name = item['name']
                    updated = True
                if obj.fromm != item['fromm']:
                    obj.fromm = item['fromm']
                    updated = True
                if obj.long != item['long']:
                    obj.long = item['long']
                    updated = True
                if updated:
                    obj.save()
                    self.stdout.write(self.style.SUCCESS(f'Formato931 "{obj.name}" updated'))
