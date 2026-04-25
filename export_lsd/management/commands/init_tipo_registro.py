import logging

from django.core.management.base import BaseCommand

from export_lsd.models import TipoRegistro
from export_lsd.tables.tabla_init_data import TABLA_TIPOREGISTRO

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize TipoRegistro table with default data'

    def handle(self, *args, **options):
        for item in TABLA_TIPOREGISTRO:
            obj, created = TipoRegistro.objects.get_or_create(
                id=item['id'],
                defaults={
                    'name': item['name'],
                    'order': item['order'],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'TipoRegistro "{obj.name}" created'))
            else:
                updated = False
                if obj.name != item['name']:
                    obj.name = item['name']
                    updated = True
                if obj.order != item['order']:
                    obj.order = item['order']
                    updated = True
                if updated:
                    obj.save()
                    self.stdout.write(self.style.SUCCESS(f'TipoRegistro "{obj.name}" updated'))
