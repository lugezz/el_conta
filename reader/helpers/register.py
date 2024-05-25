import os

from export_lsd.models import BulkCreateManager
from reader.helpers.lectores import extended_leeXML
from reader.models import RegAcceso, Registro


def RegistraCarpetaXML(usuario, full_folder):
    # Creo el registro en RegAccesos
    registro = RegAcceso.objects.create(reg_user=usuario)
    id_reg = registro.id

    for filename in os.listdir(full_folder):
        if filename.endswith(".xml"):
            ffile = os.path.join(full_folder, filename)
            empleado = extended_leeXML(ffile)

            add_registro_empleado(empleado, registro)

    return id_reg


def add_registro_empleado(empleado, instancia_bd):
    cuit = empleado.cuit
    presentacion_version = empleado.presentacion_version
    bulk_mgr = BulkCreateManager()

    # Deducciones ---------------------------------
    if empleado.deducciones:
        for deduc in empleado.deducciones:
            deduccion = deduc['nombre']
            tipo = deduc['tipo']
            dato1 = deduc['subtipo']
            dato2 = deduc['importe']
            porc = deduc['porc']
            nro_doc = deduc['nro_doc']
            mes = deduc['mes'] or None

            bulk_mgr.add(Registro(
                id_reg=instancia_bd,
                cuil=cuit,
                deduccion=deduccion,
                tipo=tipo,
                dato1=dato1,
                dato2=dato2,
                porc=porc,
                nro_doc=nro_doc,
                mes=mes,
                presentacion_version=presentacion_version,
            ))

    # Cargas de Familia ---------------------------------
    if empleado.cargasFamilia:
        for carga_flia in empleado.cargasFamilia:
            deduccion = carga_flia['nombre']
            tipo = carga_flia['tipo']
            dato1 = carga_flia['desde']
            dato2 = carga_flia['hasta']
            porc = carga_flia['porc']

            bulk_mgr.add(Registro(
                id_reg=instancia_bd,
                cuil=cuit,
                deduccion=deduccion,
                tipo=tipo,
                dato1=dato1,
                dato2=dato2,
                porc=porc,
                presentacion_version=presentacion_version,
            ))

    # Ganancia Otros Empleadores ---------------------------------
    if empleado.ganLiqOtrosEmpEnt:
        for gan_oe in empleado.ganLiqOtrosEmpEnt:
            deduccion = gan_oe['nombre']
            tipo = gan_oe['tipo']
            dato1 = 0
            dato2 = gan_oe['importe']
            porc = 0
            mes = gan_oe['mes']
            nro_doc = gan_oe['nro_doc']

            bulk_mgr.add(Registro(
                id_reg=instancia_bd,
                cuil=cuit,
                deduccion=deduccion,
                tipo=tipo,
                dato1=dato1,
                dato2=dato2,
                porc=porc,
                presentacion_version=presentacion_version,
                nro_doc=nro_doc,
                mes=mes,
            ))

    # Percepciones ---------------------------------
    if empleado.retPerPagos:
        for percepcion in empleado.retPerPagos:
            deduccion = percepcion['nombre']
            tipo = percepcion['tipo']
            dato1 = 0
            dato2 = percepcion['importe']
            porc = 0
            nro_doc = percepcion['nro_doc']
            mes = percepcion['mes']

            bulk_mgr.add(Registro(
                id_reg=instancia_bd,
                cuil=cuit,
                deduccion=deduccion,
                tipo=tipo,
                dato1=dato1,
                dato2=dato2,
                porc=porc,
                nro_doc=nro_doc,
                mes=mes,
                presentacion_version=presentacion_version,
            ))
    # Guardo en BD
    bulk_mgr.done()
