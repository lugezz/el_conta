from datetime import datetime
import os
import zipfile

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from pathlib import Path
import pytz
import shutil

from reader.helpers.lectores import leeXML
from reader.helpers.register import RegistraCarpetaXML
from reader.helpers.reporters import QueryToExc
from reader.models import RegAcceso, Registro


def get_carpeta(usuario):
    archivo_path = os.path.join('carpetas/', f'ultima_carpeta {usuario}.txt')
    with open(archivo_path, "r") as f:
        carpeta = f.readlines()

    return Path(carpeta[0])


@login_required
def siradig_view(request):
    listado = {}
    query_historia = RegAcceso.objects.filter(reg_user=request.user)

    if request.method == 'POST' and request.FILES.get('upload'):
        # TODO: Validar form
        listado = lista_zip(request.FILES['upload'])
        dire = lista_zip_ex(request.FILES['upload'])
        if not os.path.exists('carpetas/'):
            os.mkdir('carpetas')

        archivo_path = os.path.join('carpetas/', f'ultima_carpeta {request.user}.txt')
        with open(archivo_path, 'w') as f:
            f.write(dire)

    else:
        # Borro los archivos en carpeta temporal de Siradig!
        siradig_temp = settings.TEMP_ROOT / "siradig/"
        clean_folder(siradig_temp, False)

    my_context = {
        'listado': listado,
        'query_historia': query_historia,
    }

    return render(request, 'reader/home.html', my_context)


@login_required
def detalle_presentacion(request, id):
    q = RegAcceso.objects.get(id=id)
    user = q.reg_user
    date_time = q.fecha
    time_zone = pytz.timezone(settings.TIME_ZONE)
    date_local = date_time.astimezone(time_zone)

    url = q.get_absolute_url()

    if request.user != user:
        return redirect(f"{reverse('no_autorizado')}?next={request.path}")

    query = Registro.objects.filter(id_reg=id)
    titulo = f'Presentación {id} - {date_local.strftime("%d/%m/%Y %H:%M")}'

    context = {
        'query': query,
        'titulo': titulo,
        'url': url,
    }

    return render(request, 'reader/detalle_presentacion.html', context)


@login_required
def archivo_solo_view(request, slug):
    # TODO: Agregar validaciones de archivos
    xml_path = os.path.join(get_carpeta(request.user), slug)
    siradig_empleado = leeXML(xml_path)

    context = {
        'siradig_empleado': siradig_empleado.get_dict_all(),
    }

    return render(request, 'reader/soloxml.html', context)


@login_required
def procesa_view(request):

    id_reg = RegistraCarpetaXML(request.user, get_carpeta(request.user))
    query = Registro.objects.filter(id_reg=id_reg)

    siradig_temp = f"{settings.TEMP_URL}siradig/"
    url_to_file = os.path.join(siradig_temp, f"Presentacion_{id_reg}.xlsx")

    my_context = {
        'titulo': 'Proceso exitoso',
        'archproc': query.count(),
        'url_to_file': url_to_file,
    }

    return render(request, 'reader/procesa.html', my_context)


def no_autorizado(request):
    return render(request, 'reader/no-autorizado.html', {})


@login_required
def procesa_hist_view(request, id=0):

    if id == 0:
        id_reg = RegistraCarpetaXML(request.user, get_carpeta(request.user))
        titulo = 'Procesado exitosamente'

    else:
        id_reg = id
        q = RegAcceso.objects.get(id=id_reg)
        user = q.reg_user
        titulo = 'Archivo listo para la descarga'

        if request.user != user:
            return redirect(f"{reverse('no_autorizado')}?next={request.path}")

    query = Registro.objects.filter(id_reg=id_reg)
    QueryToExc(id_reg, query)

    siradig_temp = f"{settings.TEMP_URL}siradig/"
    url_to_file = os.path.join(siradig_temp, f"Presentacion_{id_reg}.xlsx")

    my_context = {
        'titulo': titulo,
        'archproc': query.count(),
        'url_to_file': url_to_file,
    }

    return render(request, 'reader/procesa.html', my_context)


def lista_zip(arch):
    zf = zipfile.ZipFile(arch, "r")
    listz = zf.namelist

    return listz


def lista_zip_ex(arch):
    zf = zipfile.ZipFile(arch, "r")
    siradig_temp = settings.TEMP_ROOT / "siradig/"
    dirx = os.path.join(siradig_temp, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    zf.extractall(path=dirx)

    return dirx


def clean_folder(path_to_folder, remove_files_too=True):
    for path in Path(path_to_folder).glob("**/*"):
        if path.is_file() and remove_files_too:
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
