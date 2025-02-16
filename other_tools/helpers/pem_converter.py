import base64
import datetime
import re
import string

import xmltodict

from other_tools.helpers.base_tools import dictionary_to_excel


string_to_remove = [
    ('\n', ''),
    ('\r', ''),
    ('@', ''),
    ('/Rporc', '/porc'),
]


def extract_xml_from_cms(pem_file_path):
    with open(pem_file_path, 'r') as file:
        pem_content = file.read()

    # Extraer solo la parte codificada en Base64
    base64_data = re.search(r"-----BEGIN CMS-----(.*?)-----END CMS-----", pem_content, re.DOTALL)
    if not base64_data:
        raise ValueError("No se encontró contenido válido en el archivo PEM")

    # Decodificar Base64
    cms_bytes = base64.b64decode(base64_data.group(1).strip())

    # Buscar el inicio del XML en los bytes decodificados
    xml_start = cms_bytes.find(b"<?xml")
    if xml_start == -1:
        raise ValueError("No se encontró contenido XML en el archivo CMS")

    xml_end = cms_bytes.find(b"</tns:auditoria>") + len(b"</tns:auditoria>")
    if xml_end == -1:
        raise ValueError("No se encontró el final del contenido XML en el archivo CMS")

    xml_content = cms_bytes[xml_start:xml_end]
    decoded_xml = xml_content.decode('utf-8', errors='ignore')

    # Filter out non-printable characters
    cleaned_string = ''.join(char for char in decoded_xml if char in string.printable)

    for char in string_to_remove:
        cleaned_string = cleaned_string.replace(char[0], char[1])

    return cleaned_string


def xml_to_dict(xml_content):
    """ Función que convierte un XML en un diccionario de Python.
    """
    diccionario_base = xmltodict.parse(xml_content)

    return diccionario_base


def get_datos_emisor_dict(xml_dict):
    """ Función que extrae los datos del emisor de un diccionario de Python.
    """
    emisor = xml_dict.get("tns:auditoria", {}).get("emisor")

    return emisor


def get_cierresZ_list(xml_dict) -> list:
    """ Función que extrae los cierres Z de un diccionario de Python.
        con todo el archivo del 8011
    """
    cierresZ_a = xml_dict.get("tns:auditoria", {}).get("arrayComprobantesAuditoria", {})
    cierresZ_b = cierresZ_a.get("comprobanteAuditoria", {}).get("arrayCierresZ", {}).get("cierreZFecha", {})

    return cierresZ_b


def get_cierresZ_dict(cierresz_list: list) -> dict:
    """ Función que arma el diccionario para ser posteriormente exportado a excel
    """
    headers = [
        'fecha', 'cierre', 'tipo', 'primer', 'ultimo', 'cantidad',
        'gravado', 'no_gravado', 'exento', 'iva0', 'iva21', 'iva105',
        'otros_tributos', 'descuentos_cod_99', 'total', 'cancelados'
    ]
    format_headers = {
        'fecha': {'title': 'Fecha', 'format': 'date', 'format_string': 'dd/mm/yyyy'},
        'gravado': {'title': 'Gravado', 'format': 'number', 'format_string': '$ #,##0.00'},
        'no_gravado': {'title': 'No Gravado', 'format': 'number', 'format_string': '$ #,##0.00'},
        'exento': {'title': 'Exento', 'format': 'number', 'format_string': '$ #,##0.00'},
        'iva0': {'title': 'IVA 0%', 'format': 'number', 'format_string': '$ #,##0.00'},
        'iva21': {'title': 'IVA 21%', 'format': 'number', 'format_string': '$ #,##0.00'},
        'iva105': {'title': 'IVA 10.5%', 'format': 'number', 'format_string': '$ #,##0.00'},
        'otros_tributos': {'title': 'Otros Tributos', 'format': 'number', 'format_string': '$ #,##0.00'},
        'descuentos_cod_99': {'title': 'Descuentos Cod. 99', 'format': 'number', 'format_string': '$ #,##0.00'},
        'total': {'title': 'Total', 'format': 'number', 'format_string': '$ #,##0.00'},

        'tipo': {'title': 'Tipo', 'format': 'number', 'format_string': '#'},
        'primer': {'title': 'Primer', 'format': 'number', 'format_string': '#'},
        'ultimo': {'title': 'Último', 'format': 'number', 'format_string': '#'},
        'cantidad': {'title': 'Cantidad', 'format': 'number', 'format_string': '#'},
        'cancelados': {'title': 'Cancelados', 'format': 'number', 'format_string': '#'},
    }
    data = []

    for cierreZ in cierresz_list:
        fecha = cierreZ.get('fechaHoraEmisionCierreZ')
        # Fecha viene como 2025-01-08T20:12:28
        fecha = datetime.datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%S')
        this_cierreZ = cierreZ.get('cierreZ', {})
        if not this_cierreZ:
            print("No hay cierreZ")
            print("---", cierreZ, "----")
            continue

        info_comprobante_base = this_cierreZ.get('arrayConjuntosComprobantesFiscales', {})
        if not info_comprobante_base:
            print("No hay info_comprobante_base")
            print("---", this_cierreZ, "----")
            continue

        info_comprobante = info_comprobante_base.get('conjuntoComprobantesFiscales', {})

        cierre = int(this_cierreZ.get('numeroZ', 0))
        tipo = int(info_comprobante.get('codigoTipoComprobante', 0))
        primer = int(info_comprobante.get('primerNumeroComprobante', 0))
        ultimo = int(info_comprobante.get('ultimoNumeroComprobante', 0))
        cantidad = int(info_comprobante.get('cantidadComprobantes', 0))
        gravado = float(info_comprobante.get('importeTotalGravado', 0))
        no_gravado = float(info_comprobante.get('importeTotalNoGravado', 0))
        exento = float(info_comprobante.get('importeTotalExento', 0))
        subtotales_iva = info_comprobante.get('arraySubtotalesIVA', {}).get('subtotalIVA', {})
        iva0 = 0
        iva21 = 0
        iva105 = 0
        # Ver cómo funciona si hay más de una alícuota
        if not isinstance(subtotales_iva, list):
            subtotales_iva = [subtotales_iva]

        for subtotal_iva in subtotales_iva:
            this_porcentaje = subtotal_iva.get('porcentajeIVA')
            if this_porcentaje == '0.00':
                iva0 += float(subtotal_iva.get('importe'))
            elif this_porcentaje == '21.00':
                iva21 += float(subtotal_iva.get('importe'))
            elif this_porcentaje == '10.50':
                iva105 += float(subtotal_iva.get('importe'))
            else:
                print("Porcentaje de IVA no reconocido:", this_porcentaje)

        otros_tributos = info_comprobante.get('arrayOtrosTributos')
        otros_tributos = otros_tributos or 0
        descuentos_cod_99 = float(info_comprobante.get('totalDescuentosCod99ComprobantesFiscales', 0))
        total = float(info_comprobante.get('importeTotalComprobantes', 0))
        cancelados = int(info_comprobante.get('cantidadComprobantesCancelados'))

        data.append({
            'fecha': fecha,
            'cierre': cierre,
            'tipo': tipo,
            'primer': primer,
            'ultimo': ultimo,
            'cantidad': cantidad,
            'gravado': gravado,
            'no_gravado': no_gravado,
            'exento': exento,
            'iva0': iva0,
            'iva21': iva21,
            'iva105': iva105,
            'otros_tributos': otros_tributos,
            'descuentos_cod_99': descuentos_cod_99,
            'total': total,
            'cancelados': cancelados,
        })

    cierresZ_dict = {
        'headers': headers,
        'data': data,
    }

    return cierresZ_dict, format_headers


def pem_to_dict(file_path) -> dict:
    """ Toma el archivo pem y extrae el XML
        Retorna toda la información en formato diccionario
    """
    # Ejecutar la función
    decoded_xml = extract_xml_from_cms(file_path)
    # Write the decoded xml to a file
    dict_xml = xml_to_dict(decoded_xml)

    return dict_xml


def dict_xml_to_excel(dict_xml, output_path):
    """ Toma el diccionario con el XML y lo convierte en un archivo Excel
    """
    cierresZ = get_cierresZ_list(dict_xml)
    cierresZ_dict, format_headers = get_cierresZ_dict(cierresZ)

    final_excel = dictionary_to_excel(cierresZ_dict, output_path, columns_format=format_headers)

    return final_excel


def convert_pem_a_excel(file_path, output_path):
    """ Toma el archivo pem, extrae el XML y lo convierte en un archivo Excel
    """
    # Convierte el archivo PEM a un diccionario de Python
    # Se dividió a fines de poder dar una vista previa de resultados antes de descargar
    dict_xml = pem_to_dict(file_path)

    # Convierte el diccionario a un archivo Excel
    final_excel = dict_xml_to_excel(dict_xml, output_path)

    return final_excel
