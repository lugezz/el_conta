from datetime import datetime
import xmltodict

import xml.etree.ElementTree as ET

from reader.deducciones import get_deduccion
from reader.helpers.tools import get_nombre_y_valor, get_list_of_values_from_list, get_value_from_list


class EmpleadoSiradig:
    def __init__(self, cuit, nro_presentacion, fecha, deducciones=[],
                 cargasFamilia=[], ganLiqOtrosEmpEnt=[], retPerPagos=[], presentacion_version=''):
        self.cuit = cuit
        self.nro_presentacion = nro_presentacion
        self.fecha = fecha
        self.deducciones = deducciones
        self.cargasFamilia = cargasFamilia
        self.ganLiqOtrosEmpEnt = ganLiqOtrosEmpEnt
        self.retPerPagos = retPerPagos
        self.presentacion_version = presentacion_version

    def get_cuit(self):
        return self.cuit

    def get_dict_all(self):
        diccionario = {
            'cuit': self.cuit,
            'deducciones': self.deducciones,
            'cargasFamilia': self.cargasFamilia,
            'ganLiqOtrosEmpEnt': self.ganLiqOtrosEmpEnt,
            'retPerPagos': self.retPerPagos,
        }

        return diccionario

    def get_total_deducciones(self):
        resp = 0
        for deduccion in self.deducciones:
            resp += deduccion['importe']


def procesar_deducciones_extended(lista_deducciones: list) -> list:
    """ Procesa las deducciones de la presentación para un empleado
        retorna una lista de diccionarios con la información de las deducciones
    """
    deducciones = []

    for deduccion in lista_deducciones:
        subtipo = 0
        ded_porc = 0
        if 'detalles' in deduccion:
            subtipo = deduccion['detalles']['detalle'][0]['@valor']

        ded_tipo = deduccion['@tipo']
        nro_doc = deduccion['nroDoc']

        # Herramientas educativas, puede tener 2 tipos
        # Otras deducciones, puede tener 9 tipos
        # Y el formato es diferente, se informa un registro por período

        if ded_tipo == '32':
            ded_detalle = deduccion['detalles']['detalle']
            info_to_get = ['porcentajeDedFamiliar', 'tipoGasto']
            info_obtenida = get_list_of_values_from_list(ded_detalle, info_to_get)
            ded_porc = info_obtenida['porcentajeDedFamiliar']
            subtipo = info_obtenida['tipoGasto']

        # Otras deducciones, puede tener 9 tipos
        # Y el formato es diferente, se informa un registro por período
        if ded_tipo == '99':
            ded_detalle = deduccion['detalles']['detalle']
            subtipo, mes = get_nombre_y_valor(ded_detalle)
            deducciones.append(
                {
                    'nombre': 'deduccion',
                    'tipo': ded_tipo,
                    'subtipo': subtipo,
                    'importe': deduccion['montoTotal'],
                    'descripcion': get_deduccion('deduccion', ded_tipo),
                    'porc': 0,
                    'nro_doc': nro_doc,
                    'mes': mes,
                }
            )
            continue

        # Herramientas educativas, puede tener 2 tipos
        if ded_tipo == '32':
            ded_detalle = deduccion['detalles']['detalle']
            info_to_get = ['porcentajeDedFamiliar', 'tipoGasto']
            info_obtenida = get_list_of_values_from_list(ded_detalle, info_to_get)
            ded_porc = info_obtenida['porcentajeDedFamiliar']
            subtipo = info_obtenida['tipoGasto']

        # Si el tipo de deducción es 9 SGR, viene de esta forma el detalle
        # [{'@nombre': 'fechaAporte', '@valor': '2023-01-09'},
        #  {'@nombre': 'montoCapSocial', '@valor': '465000'},
        #  {'@nombre': 'montoFondoRiesgo', '@valor': '465000'}
        # ]
        if ded_tipo == '9':
            subtipo = 0
            ded_detalle = deduccion['detalles']['detalle']
            ded_porc, fecha = get_nombre_y_valor(ded_detalle, '', 'fechaAporte')
            # fecha viene con el formato '2023-01-09', tomo el mes
            mes = int(fecha.split('-')[1])

            deducciones.append(
                {
                    'nombre': 'deduccion',
                    'tipo': ded_tipo,
                    'subtipo': subtipo,
                    'importe': deduccion['montoTotal'],
                    'descripcion': get_deduccion('deduccion', ded_tipo),
                    'porc': ded_porc,
                    'nro_doc': nro_doc,
                    'mes': mes,
                }
            )
            continue

        # En este lee extended, se toma el detalle de las deducciones periodo por periodo
        # Para todas las deducciones que no sean 32, 99 y 9
        periodos = deduccion['periodos']['periodo']

        # Si hay un solo periodo no lo hace lista, lo adapto
        if not isinstance(periodos, list):
            periodos = [periodos]

        for periodo in periodos:
            desde = periodo['@mesDesde']
            hasta = periodo['@mesHasta']
            importe = periodo['@montoMensual']

            for i in range(int(desde), int(hasta) + 1):
                deducciones.append(
                    {
                        'nombre': 'deduccion',
                        'tipo': ded_tipo,
                        'subtipo': subtipo,
                        'importe': importe,
                        'descripcion': get_deduccion('deduccion', ded_tipo),
                        'porc': ded_porc,
                        'nro_doc': nro_doc,
                        'mes': i
                    }
                )

    return deducciones


def procesas_percepciones_extended(lista_percepciones: list) -> list:
    """ Procesa las percepciones de la presentación para un empleado
        retorna una lista de diccionarios con la información de las percepciones
    """
    percepciones = []

    for percepcion in lista_percepciones:
        # En este lee extended, se toma el detalle de las deducciones periodo por periodo
        periodos = percepcion['periodos']['periodo']
        nro_doc = percepcion['nroDoc']
        perc_tipo = percepcion['@tipo']

        # Si hay un solo periodo no lo hace lista, lo adapto
        if not isinstance(periodos, list):
            periodos = [periodos]

        for periodo in periodos:
            desde = periodo['@mesDesde']
            hasta = periodo['@mesHasta']
            importe = periodo['@montoMensual']

            for i in range(int(desde), int(hasta) + 1):
                percepciones.append(
                    {
                        'nombre': 'retPerPago',
                        'tipo': perc_tipo,
                        'importe': importe,
                        'descripcion': get_deduccion('retPerPago', percepcion['@tipo']),
                        'nro_doc': nro_doc,
                        'mes': i,
                    }
                )

    return percepciones


def procesa_ganancias_otros_emp_ent(lista_gan_otro_emp: list) -> list:
    """ Procesa las ganancias de otros empleadores de la presentación para un empleado
        retorna una lista de diccionarios con la información de las ganancias
    """
    ganLiqOtrosEmpEnt = []
    for ganancia_OE in lista_gan_otro_emp:
        lista_ingresos = ganancia_OE['ingresosAportes']['ingAp']
        nro_doc = ganancia_OE['cuit']

        if not isinstance(lista_ingresos, list):
            # Cuando hay un solo registro no lo hace lista, lo adapto
            lista_ingresos = [lista_ingresos]

        for ganancia_mes_OE in lista_ingresos:
            for item in ganancia_mes_OE:
                mes = ganancia_mes_OE.get('@mes', 0)
                if ganancia_mes_OE[item] != '0' and item != '@mes':
                    ganLiqOtrosEmpEnt.append(
                        {
                            'nombre': 'ganLiqOtrosEmpEnt',
                            'tipo': item,
                            'importe': ganancia_mes_OE[item],
                            'nro_doc': nro_doc,
                            'mes': mes,
                        }
                    )

    return ganLiqOtrosEmpEnt


def procesa_deducciones(lista_deducciones: list) -> list:
    """ Procesa las deducciones de la presentación para un empleado
        retorna una lista de diccionarios con la información de las deducciones
    """
    deducciones = []

    for deduccion in lista_deducciones:
        subtipo = 0
        if 'detalles' in deduccion:
            subtipo = deduccion['detalles']['detalle'][0]['@valor']

        ded_tipo = deduccion['@tipo']

        if ded_tipo == '32':
            ded_detalle = deduccion['detalles']['detalle']
            ded_porc = get_value_from_list(ded_detalle, 'porcentajeDedFamiliar')
        else:
            ded_porc = 0

        deducciones.append(
            {
                'nombre': 'deduccion',
                'tipo': ded_tipo,
                'subtipo': subtipo,
                'importe': deduccion['montoTotal'],
                'descripcion': get_deduccion('deduccion', ded_tipo),
                'porc': ded_porc
            }
        )

    return deducciones


def procesa_ganancias_otros_emp(lista_gan_otro_emp: list) -> list:
    """ Procesa las ganancias de otros empleadores de la presentación para un empleado
        retorna una lista de diccionarios con la información de las ganancias
    """
    ganLiqOtrosEmpEnt = []

    for ganancia_OE in lista_gan_otro_emp:
        lista_ingresos = ganancia_OE['ingresosAportes']['ingAp']
        if not isinstance(lista_ingresos, list):
            # Cuando hay un solo registro no lo hace listo, lo adapto
            lista_ingresos = [lista_ingresos]

        for ganancia_mes_OE in lista_ingresos:
            for item in ganancia_mes_OE:

                if ganancia_mes_OE[item] != '0' and item != '@mes':
                    ganLiqOtrosEmpEnt.append(
                        {
                            'nombre': 'ganLiqOtrosEmpEnt',
                            'tipo': item,
                            'importe': ganancia_mes_OE[item],
                        }
                    )
    return ganLiqOtrosEmpEnt


def leeXML(xml_file):
    """
    Lee XML
    ------
    Devuelve un objeto Empleado con la información
    de la presentación y todo lo declarado
    """

    tree = ET.parse(xml_file)
    xml_data = tree.getroot()
    xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')

    diccionario_base = xmltodict.parse(xmlstr)
    cuit = diccionario_base['presentacion']['empleado']['cuit']
    nro_presentacion = diccionario_base['presentacion']['nroPresentacion']
    fecha = diccionario_base['presentacion']['fechaPresentacion']
    fecha = datetime.strptime(fecha, '%Y-%m-%d')
    deducciones = []
    cargasFamilia = []
    ganLiqOtrosEmpEnt = []
    retPerPagos = []

    # Tomo Deducciones -----------------------------------
    if diccionario_base['presentacion'].get('deducciones'):
        lista_deducciones = diccionario_base['presentacion']['deducciones']['deduccion']
        if not isinstance(lista_deducciones, list):
            # Para que el bucle no tome los campos
            lista_deducciones = [lista_deducciones]

        deducciones = procesa_deducciones(lista_deducciones)

    # Tomo Cargas de Familia -----------------------------------
    if diccionario_base['presentacion'].get('cargasFamilia'):
        lista_familiares = diccionario_base['presentacion']['cargasFamilia']['cargaFamilia']

        if not isinstance(lista_familiares, list):
            # Para que el bucle no tome los campos
            lista_familiares = [lista_familiares]

        for carga_flia in lista_familiares:
            cargasFamilia.append(
                {
                    'nombre': 'cargaFamilia',
                    'tipo': carga_flia['parentesco'],
                    'desde': carga_flia['mesDesde'],
                    'hasta': carga_flia['mesHasta'],
                    'porc': carga_flia['porcentajeDeduccion'],
                    'descripcion': get_deduccion('cargaFamilia', carga_flia['parentesco'])
                 }
            )

    # Tomo Ganancias otros empleadores -----------------------------------
    if diccionario_base['presentacion'].get('ganLiqOtrosEmpEnt'):
        lista_gan_otro_emp = diccionario_base['presentacion']['ganLiqOtrosEmpEnt']['empEnt']

        if not isinstance(lista_gan_otro_emp, list):
            # Para que el bucle no tome los campos
            lista_gan_otro_emp = [lista_gan_otro_emp]

        ganLiqOtrosEmpEnt = procesa_ganancias_otros_emp(lista_gan_otro_emp)

    # Tomo Percepciones -----------------------------------
    if diccionario_base['presentacion'].get('retPerPagos'):
        lista_percepciones = diccionario_base['presentacion']['retPerPagos']['retPerPago']

        if not isinstance(lista_percepciones, list):
            # Para que el bucle no tome los campos
            lista_percepciones = [lista_percepciones]

        for percepcion in lista_percepciones:
            retPerPagos.append(
                {'nombre': 'retPerPago',
                 'tipo': percepcion['@tipo'],
                 'importe': percepcion['montoTotal'],
                 'descripcion': get_deduccion('retPerPago', percepcion['@tipo'])
                 }
            )

    empleado = EmpleadoSiradig(cuit=cuit,
                               nro_presentacion=nro_presentacion,
                               fecha=fecha,
                               deducciones=deducciones,
                               cargasFamilia=cargasFamilia,
                               ganLiqOtrosEmpEnt=ganLiqOtrosEmpEnt,
                               retPerPagos=retPerPagos)

    return empleado


def extended_leeXML(xml_file):
    """
    Lee XML Extended
    ------
    Devuelve un objeto Empleado con la información de la presentación y todo lo declarado
    Aquí se incluye registro por registro en vez de los totales que informaba la versión anterior (leeXML)
    """

    tree = ET.parse(xml_file)
    xml_data = tree.getroot()
    xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')

    # Parseo el XML en un diccionario
    diccionario_base = xmltodict.parse(xmlstr)

    # Tomo los datos de la presentación
    cuit = diccionario_base['presentacion']['empleado']['cuit']
    nro_presentacion = diccionario_base['presentacion']['nroPresentacion']
    presentacion_version = diccionario_base['presentacion'].get('@version')
    fecha = diccionario_base['presentacion']['fechaPresentacion']
    fecha = datetime.strptime(fecha, '%Y-%m-%d')

    cargasFamilia = []
    deducciones = []
    ganLiqOtrosEmpEnt = []
    retPerPagos = []

    # Info de la presentación
    deducciones_xml = diccionario_base['presentacion'].get('deducciones')

    # Tomo Deducciones --------------------------------------------------------------
    if deducciones_xml:
        lista_deducciones = deducciones_xml['deduccion']

        if not isinstance(lista_deducciones, list):
            # En los casos de un solo registro no lo hace lista, lo adapto
            lista_deducciones = [lista_deducciones]

        deducciones = procesar_deducciones_extended(lista_deducciones=lista_deducciones)

    # Tomo Cargas de Familia -----------------------------------
    if diccionario_base['presentacion'].get('cargasFamilia'):
        lista_familiares = diccionario_base['presentacion']['cargasFamilia']['cargaFamilia']

        if not isinstance(lista_familiares, list):
            # Si no es lista lo adapto, cuando es sólo un registro sucede esto
            lista_familiares = [lista_familiares]

        for carga_flia in lista_familiares:
            cargasFamilia.append(
                {'nombre': 'cargaFamilia',
                 'tipo': carga_flia['parentesco'],
                 'desde': carga_flia['mesDesde'],
                 'hasta': carga_flia['mesHasta'],
                 'porc': carga_flia['porcentajeDeduccion'],
                 'descripcion': get_deduccion('cargaFamilia', carga_flia['parentesco'])
                 }
            )

    # Tomo Ganancias otros empleadores -----------------------------------
    if diccionario_base['presentacion'].get('ganLiqOtrosEmpEnt'):
        lista_gan_otro_emp = diccionario_base['presentacion']['ganLiqOtrosEmpEnt']['empEnt']

        if not isinstance(lista_gan_otro_emp, list):
            # Si sólo hay un registro no lo hace lista, lo adapto
            lista_gan_otro_emp = [lista_gan_otro_emp]

        ganLiqOtrosEmpEnt = procesa_ganancias_otros_emp_ent(lista_gan_otro_emp)

    # Tomo Percepciones -----------------------------------
    if diccionario_base['presentacion'].get('retPerPagos'):
        lista_percepciones = diccionario_base['presentacion']['retPerPagos']['retPerPago']

        if not isinstance(lista_percepciones, list):
            # Si sólo hay un registro no lo hace lista, lo adapto
            lista_percepciones = [lista_percepciones]

        retPerPagos = procesas_percepciones_extended(lista_percepciones)

    empleado = EmpleadoSiradig(
        cuit=cuit,
        nro_presentacion=nro_presentacion,
        fecha=fecha,
        deducciones=deducciones,
        cargasFamilia=cargasFamilia,
        ganLiqOtrosEmpEnt=ganLiqOtrosEmpEnt,
        retPerPagos=retPerPagos,
        presentacion_version=presentacion_version,
    )

    return empleado
