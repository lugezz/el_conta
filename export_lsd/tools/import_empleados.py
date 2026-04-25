import logging
import re
from pathlib import Path

import pandas as pd
from django.db import IntegrityError, connection
from django.db.models import Max
from django.utils.functional import SimpleLazyObject

from export_lsd.models import BulkCreateManager, Empleado, Empresa

logger = logging.getLogger(__name__)

INFO_EMPLEADOS_MIN_COLUMNS = {
    'Leg',
    'CUIL',
    'CBU',
}


def is_positive_number(str_num: str) -> bool:
    num_format = "^\\d+$"

    return re.match(num_format, str_num)


def get_employees(file_import: Path, this_user: SimpleLazyObject) -> dict:
    employees_dict = {
        'error': '',
        'results': set(),
        'invalid_data': [],
    }

    df = pd.read_excel(file_import)

    for index, row in df.iterrows():

        if not is_positive_number(str(row['CUIT Empresa'])) or len(str(row['CUIT Empresa'])) != 11:
            employees_dict['invalid_data'].append(f"Línea: {index} - CUIT {row['CUIT Empresa']} Inválido")
            continue

        if not get_company_name(row['CUIT Empresa'], this_user):
            employees_dict['invalid_data'].append(f"Línea: {index} - CUIT {row['CUIT Empresa']} inexistente")
            continue

        if not is_positive_number(str(row['CUIL'])) or len(str(row['CUIL'])) != 11:
            employees_dict['invalid_data'].append(f"Línea: {index} - CUIL {row['CUIL']} Inválido")
            continue

        if not is_positive_number(str(row['Leg'])):
            employees_dict['invalid_data'].append(f"Línea: {index} - L.{row['Leg']} Inválido")
            continue

        if get_empleado_name(str(row['CUIT Empresa']), str(row['Leg']), this_user):
            employees_dict['invalid_data'].append(f"Línea: {index} - L.{row['Leg']} - CUIT {row['CUIT Empresa']} ya existe")
            continue

        # Todo ok aquí
        employees_dict['results'].add((row['CUIT Empresa'], row['Leg'], row['Nombre'], row['CUIL'], row['Area']))

    # Results as list to make it JSON seriazable
    employees_dict['results'] = list(employees_dict['results'])

    return employees_dict


def get_company_name(cuit: str, this_user: SimpleLazyObject) -> str:
    qs = Empresa.objects.filter(cuit=cuit, user=this_user)

    res = '' if not qs else qs.first().name

    return res


def get_empleado_name(cuit: str, leg: str, this_user: SimpleLazyObject) -> str:
    qs = Empleado.objects.filter(leg=leg, empresa__cuit=cuit, empresa__user=this_user)

    res = '' if not qs else qs.first().name

    return res


def bulk_new_employees(user: SimpleLazyObject, employees_data: list):
    """
    Registra de manera masiva empleados
    formato:[
        [CUIT, Leg, Nombre, CUIL, Área]
        .....
    ]
    """

    bulk_mgr = BulkCreateManager()

    for item in employees_data:
        empresa = Empresa.objects.get(cuit=item[0], user=user)
        bulk_mgr.add(Empleado(empresa=empresa, leg=item[1], name=item[2], cuil=item[3], area=item[4]))

    _bulk_insert_with_sequence_sync(bulk_mgr)


def _sync_pk_sequence(model_class):
    if connection.vendor != 'postgresql':
        return

    table_name = model_class._meta.db_table
    pk_column = model_class._meta.pk.column
    max_id = model_class.objects.aggregate(max_id=Max(pk_column)).get('max_id') or 0

    with connection.cursor() as cursor:
        cursor.execute('SELECT pg_get_serial_sequence(%s, %s)', [table_name, pk_column])
        row = cursor.fetchone()
        seq_name = row[0] if row else None

        if not seq_name:
            return

        if max_id <= 0:
            cursor.execute('SELECT setval(%s, %s, %s)', [seq_name, 1, False])
        else:
            cursor.execute('SELECT setval(%s, %s, %s)', [seq_name, max_id, True])


def _bulk_insert_with_sequence_sync(bulk_mgr: BulkCreateManager):
    _sync_pk_sequence(Empleado)

    try:
        bulk_mgr.done()
    except IntegrityError as err:
        err_msg = str(err)
        if 'export_lsd_empleado_pkey' not in err_msg:
            raise

        logger.warning('Empleado PK sequence desync detected, trying one sequence resync and retry')
        _sync_pk_sequence(Empleado)
        bulk_mgr.done()


def new_employees_from_xlsx(filepath: str, empresa: SimpleLazyObject):
    """
    Registra de manera masiva empleados informados desde excel
    """

    try:
        df = pd.read_excel(filepath)
    except Exception as err:
        raise ValueError(f'No se pudo leer el archivo Excel de empleados: {err}')

    missing_columns = INFO_EMPLEADOS_MIN_COLUMNS.difference(df.columns)
    if missing_columns:
        missing_str = ', '.join(sorted(missing_columns))
        raise ValueError(f'El archivo Excel no contiene columnas obligatorias: {missing_str}')

    bulk_mgr = BulkCreateManager()

    for index, row in df.iterrows():
        # Puede suceder que haya filas sin información y que de todas formas se lea, por eso
        # Si leg es NaN, no lo tomo y termino el loop
        if pd.isna(row['Leg']):
            break
        # En caso de que el CUIL se informe como float lo cambio a int
        if isinstance(row['CUIL'], float):
            row['CUIL'] = int(row['CUIL'])
        cbu = None if pd.isna(row['CBU']) else row['CBU']
        if Empleado.objects.filter(leg=row['Leg'], empresa=empresa).count() == 0:
            bulk_mgr.add(Empleado(empresa=empresa, leg=row['Leg'], name="Creado por Importación",
                                  cuil=row['CUIL'], area='', cbu=cbu))
        else:
            # Existe, lo actualizo. Debe ser sólo 1 registro
            this_empleado = Empleado.objects.get(leg=row['Leg'], empresa=empresa)
            this_empleado.cuil = str(row['CUIL'])
            this_empleado.cbu = str(cbu)
            this_empleado.save()
    _bulk_insert_with_sequence_sync(bulk_mgr)
