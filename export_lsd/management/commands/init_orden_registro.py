import logging

from django.core.management.base import BaseCommand

from export_lsd.models import Formato931, OrdenRegistro, TipoRegistro
from export_lsd.tables.tabla_init_data import TABLA_ORDENREGISTRO

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize OrdenRegistro table with default data'

    def handle(self, *args, **options):
        for item in TABLA_ORDENREGISTRO:
            tiporegistro = TipoRegistro.objects.get(id=item['tiporegistro_id'])
            formatof931 = None
            if item['formatof931_id'] is not None:
                formatof931 = Formato931.objects.get(id=item['formatof931_id'])

            obj, created = OrdenRegistro.objects.get_or_create(
                id=item['id'],
                defaults={
                    'tiporegistro': tiporegistro,
                    'formatof931': formatof931,
                    'name': item['name'],
                    'fromm': item['fromm'],
                    'long': item['long'],
                    'type': item['type'],
                    'description': item['description'],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'OrdenRegistro "{obj.name}" created'))
            else:
                updated = False
                for field, val in [
                    ('name', item['name']),
                    ('fromm', item['fromm']),
                    ('long', item['long']),
                    ('type', item['type']),
                    ('description', item['description']),
                ]:
                    if getattr(obj, field) != val:
                        setattr(obj, field, val)
                        updated = True
                if obj.tiporegistro_id != item['tiporegistro_id']:
                    obj.tiporegistro = tiporegistro
                    updated = True
                if obj.formatof931_id != item['formatof931_id']:
                    obj.formatof931 = formatof931
                    updated = True
                if updated:
                    obj.save()
                    self.stdout.write(self.style.SUCCESS(f'OrdenRegistro "{obj.name}" updated'))
