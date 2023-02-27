from datetime import datetime
import os
import xmltodict

from django.conf import settings
import xlsxwriter
import xml.etree.ElementTree as ET

from .models import RegAcceso, Registro
from .deducciones import get_deduccion

DEDUCCIONES_CON_SUBINDICE = ['32']


class EmpleadoSiradig:
    def __init__(self, cuit, nro_presentacion, fecha, deducciones=[],
                 cargasFamilia=[], ganLiqOtrosEmpEnt=[], retPerPagos=[]):
        self.cuit = cuit
        self.nro_presentacion = nro_presentacion
        self.fecha = fecha
        self.deducciones = deducciones
        self.cargasFamilia = cargasFamilia
        self.ganLiqOtrosEmpEnt = ganLiqOtrosEmpEnt
        self.retPerPagos = retPerPagos

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


def get_value_from_list(list_of_values: list, value_name: str):
    resp = ''

    for value in list_of_values:
        if value['@nombre'] == value_name:
            resp = value['@valor']

    return resp


def RegistraCarpetaXML(usuario, full_folder):
    # Creo el registro en RegAccesos
    registro = RegAcceso.objects.create(reg_user=usuario)
    registro.save()
    id_reg = registro.id

    for filename in os.listdir(full_folder):
        if filename.endswith(".xml"):
            ffile = os.path.join(full_folder, filename)
            empleado = leeXML(ffile)

            add_registro_empleado(empleado, registro)

    return id_reg


def add_registro_empleado(empleado, instancia_bd):
    cuit = empleado.cuit
    # Deducciones ---------------------------------
    if empleado.deducciones:
        for deduc in empleado.deducciones:
            deduccion = deduc['nombre']
            tipo = deduc['tipo']
            dato1 = deduc['subtipo']
            dato2 = deduc['importe']
            porc = deduc['porc']

            reg_ded = Registro.objects.create(id_reg=instancia_bd,
                                              cuil=cuit,
                                              deduccion=deduccion,
                                              tipo=tipo,
                                              dato1=dato1,
                                              dato2=dato2,
                                              porc=porc
                                              )
            reg_ded.save()

    # Cargas de Familia ---------------------------------
    if empleado.cargasFamilia:
        for carga_flia in empleado.cargasFamilia:
            deduccion = carga_flia['nombre']
            tipo = carga_flia['tipo']
            dato1 = carga_flia['desde']
            dato2 = carga_flia['hasta']
            porc = carga_flia['porc']

            reg_cfa = Registro.objects.create(id_reg=instancia_bd,
                                              cuil=cuit,
                                              deduccion=deduccion,
                                              tipo=tipo,
                                              dato1=dato1,
                                              dato2=dato2,
                                              porc=porc
                                              )
            reg_cfa.save()

    # Ganancia Otros Empleadores ---------------------------------
    if empleado.ganLiqOtrosEmpEnt:
        for gan_oe in empleado.ganLiqOtrosEmpEnt:
            deduccion = gan_oe['nombre']
            tipo = gan_oe['tipo']
            dato1 = 0
            dato2 = gan_oe['importe']
            porc = 0

            reg_goe = Registro.objects.create(id_reg=instancia_bd,
                                              cuil=cuit,
                                              deduccion=deduccion,
                                              tipo=tipo,
                                              dato1=dato1,
                                              dato2=dato2,
                                              porc=porc
                                              )
            reg_goe.save()

    # Percepciones ---------------------------------
    if empleado.retPerPagos:
        for percepcion in empleado.retPerPagos:
            deduccion = percepcion['nombre']
            tipo = percepcion['tipo']
            dato1 = 0
            dato2 = percepcion['importe']
            porc = 0

            reg_per = Registro.objects.create(id_reg=instancia_bd,
                                              cuil=cuit,
                                              deduccion=deduccion,
                                              tipo=tipo,
                                              dato1=dato1,
                                              dato2=dato2,
                                              porc=porc
                                              )
            reg_per.save()


def QueryToExc(id, query):
    siradig_temp = settings.TEMP_ROOT / "siradig/"
    opath = os.path.join(siradig_temp, f"Presentacion_{id}.xlsx")

    workbook = xlsxwriter.Workbook(opath)
    worksheet = workbook.add_worksheet()

    money = workbook.add_format({'num_format': '$#,##0.00'})
    header_format = workbook.add_format({'bold': True,
                                         'align': 'center',
                                         'valign': 'vcenter',
                                         'fg_color': '#D7E4BC',
                                         'border': 1})
    center_format = workbook.add_format({'align': 'center'})
    no_format = workbook.add_format()

    center_format.set_font_name('Arial')
    center_format.set_font_size(8)
    header_format.set_font_name('Arial')
    header_format.set_font_size(8)
    money.set_font_name('Arial')
    money.set_font_size(8)
    no_format.set_font_name('Arial')
    no_format.set_font_size(8)

    # Empiezo por el encabezado
    row = 1
    worksheet.write(0, 0, "CUIL", header_format)
    worksheet.write(0, 1, "Deducción", header_format)
    worksheet.write(0, 2, "Tipo", header_format)
    worksheet.write(0, 3, "Dato1", header_format)
    worksheet.write(0, 4, "Dato2", header_format)
    worksheet.write(0, 5, "Porc", header_format)
    worksheet.write(0, 6, "Descripción", header_format)

    # Algo de formato
    worksheet.set_column('A:A', 12)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('E:E', 12)
    worksheet.set_column('G:G', 60)
    worksheet.freeze_panes(1, 1)

    # Itero por cada item de MatrizTodo
    for item in query:
        worksheet.write_number(row, 0, item.cuil, center_format)
        worksheet.write(row, 1, item.deduccion, no_format)

        if item.deduccion == 'ganLiqOtrosEmpEnt':
            worksheet.write(row, 2, item.tipo, no_format)
        else:
            val_item = 0 if not item.tipo else float(item.tipo)
            worksheet.write_number(row, 2, val_item, center_format)

        val_item = 0 if not item.dato1 else int(item.dato1)
        worksheet.write_number(row, 3, int(val_item), center_format)

        if item.deduccion == 'cargaFamilia':
            worksheet.write_number(row, 4, int(item.dato2), center_format)
        else:
            worksheet.write_number(row, 4, float(item.dato2), money)

        val_item = 0 if not item.porc else float(item.porc)
        worksheet.write_number(row, 5, val_item, center_format)

        subindice = item.dato1 if item.tipo in DEDUCCIONES_CON_SUBINDICE else ''
        worksheet.write(row, 6, get_deduccion(item.deduccion, item.tipo, subindice), no_format)
        row += 1
    workbook.close()


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
        if type(lista_deducciones) != list:
            # Para que el bucle no tome los campos
            lista_deducciones = [lista_deducciones]

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
                {'nombre': 'deduccion',
                 'tipo': ded_tipo,
                 'subtipo': subtipo,
                 'importe': deduccion['montoTotal'],
                 'descripcion': get_deduccion('deduccion', ded_tipo),
                 'porc': ded_porc
                 }
            )

    # Tomo Cargas de Familia -----------------------------------
    if diccionario_base['presentacion'].get('cargasFamilia'):
        lista_familiares = diccionario_base['presentacion']['cargasFamilia']['cargaFamilia']

        if type(lista_familiares) != list:
            # Para que el bucle no tome los campos
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

        if type(lista_gan_otro_emp) != list:
            # Para que el bucle no tome los campos
            lista_gan_otro_emp = [lista_gan_otro_emp]

        for ganancia_OE in lista_gan_otro_emp:
            lista_ingresos = ganancia_OE['ingresosAportes']['ingAp']
            if type(lista_ingresos) != list:
                # Cuando hay un solo registro no lo hace listo, lo adapto
                lista_ingresos = [lista_ingresos]

            for ganancia_mes_OE in lista_ingresos:
                for item in ganancia_mes_OE:

                    if ganancia_mes_OE[item] != '0' and item != '@mes':
                        ganLiqOtrosEmpEnt.append(
                            {'nombre': 'ganLiqOtrosEmpEnt',
                             'tipo': item,
                             'importe': ganancia_mes_OE[item],
                             }
                        )
    # Tomo Percepciones -----------------------------------
    if diccionario_base['presentacion'].get('retPerPagos'):
        lista_percepciones = diccionario_base['presentacion']['retPerPagos']['retPerPago']

        if type(lista_percepciones) != list:
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
