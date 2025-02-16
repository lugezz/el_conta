import datetime
import os
import tempfile

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError

from other_tools.helpers.pem_converter import dict_xml_to_excel, pem_to_dict


# Pem a excel Import -------------------------------------------------------------------------
def handle_uploaded_pem(file_pem):
    """ Save the uploaded PEM file to a temporary file and process it """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pem") as temp_file:
        for chunk in file_pem.chunks():
            temp_file.write(chunk)
        temp_file_path = temp_file.name

    return temp_file_path


def import_pem(request):
    """ Importar PEM desde un archivo excel"""

    result_import = {
        'error': '',
        'results_data': '',
        'invalid_data': '',
        'sumary': {},
    }
    context = {
        'result_import': result_import,
        'new_file_url': '',
    }

    if request.method == 'POST':
        redirect_url = reverse('pem-a-excel')
        # Confirmation button
        if request.POST.get('has_confirmation') == 'Yes':
            data = request.session['all_data']
            datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"descarga_pem_{datetime_str}.xlsx"
            file_path = os.path.join(settings.PATH_IMPORT_8011, file_name)

            dict_xml_to_excel(dict_xml=data, output_path=file_path)
            messages.success(request, 'Archivo importado correctamente')

            response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
            # Elimino el archivo
            os.remove(file_path)
            return response

        else:
            try:
                file_pem = request.FILES['file_pem']
                temp_file_pem = handle_uploaded_pem(file_pem)
                result_import = pem_to_dict(
                    file_path=temp_file_pem,
                )
            except ValueError:
                result_import['error'] = "Formato de archivo incorrecto"
            except MultiValueDictKeyError:
                result_import['error'] = "No se ha seleccionado un archivo para importar"
            except Exception as err:
                result_import['error'] = f'{type(err)} - {err}'

            error = result_import.get('error')
            if error:
                messages.error(request, error)
                return redirect(redirect_url)

            base_dict = result_import.get('tns:auditoria', {})
            emisor = base_dict.get('emisor', {})
            comprobantes = base_dict.get('arrayComprobantesAuditoria', []).get('comprobanteAuditoria', {})
            rango = comprobantes.get('rangoSolicitado', {})
            cantidad_comprobantes = comprobantes.get('cantidadComprobantesFiscales', 0)
            total_gravado = comprobantes.get('totalGravadoComprobantesFiscales', 0)
            total_no_gravado = comprobantes.get('totalNoGravadoComprobantesFiscales', 0)
            total_exento = comprobantes.get('totalExentoComprobantesFiscales', 0)

            summary = {
                'nombre_fantasia': emisor.get('nombreFantasiaEmisor', ''),
                'razon_social': emisor.get('razonSocialEmisor', ''),
                'cuit': emisor.get('cuitEmisor', ''),
                'punto_venta': emisor.get('numeroPuntoVenta', ''),
                'desde': rango.get('fechaZDesde', ''),
                'hasta': rango.get('fechaZHasta', ''),
                'cantidad_comprobantes': cantidad_comprobantes,
                'total_gravado': total_gravado,
                'total_no_gravado': total_no_gravado,
                'total_exento': total_exento,
            }
            result_import['sumary'] = summary

            request.session['all_data'] = result_import

    context['result_import'] = result_import

    return render(request, 'other_tools/import_8011.html', context)
