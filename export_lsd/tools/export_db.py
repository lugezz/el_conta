import csv

from django.shortcuts import redirect

from export_lsd.models import Formato931, OrdenRegistro, TipoRegistro


def exportaDB(request):
    # First delete all records
    OrdenRegistro.objects.all().delete()

    reader = csv.DictReader(open("orden_registros.csv"))
    for raw in reader:
        tr = TipoRegistro.objects.get(id=raw['Tipo'])
        print(raw)
        p = OrdenRegistro(
            tiporegistro=tr,
            name=raw['Campo'],
            fromm=raw['Desde'],
            long=raw['Long'],
            type=raw['Tipo2'],
            description=raw['Observación'],
        )

        p.save()

    return redirect('export_lsd:home')


def exportaDB_f931(request):
    # First delete all records
    Formato931.objects.all().delete()

    reader = csv.DictReader(open("formato_f931.csv"))
    for raw in reader:
        print(raw)
        p = Formato931(
            name=raw['Concepto'],
            fromm=raw['Desde'],
            long=raw['Largo'],
        )

        p.save()

    return redirect('export_lsd:home')
