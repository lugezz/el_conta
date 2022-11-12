import re

from django.utils.functional import SimpleLazyObject
import pandas as pd
from pathlib import Path

from export_lsd.models import Empleado, Empresa


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
