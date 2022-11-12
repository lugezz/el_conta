from datetime import date

from export_lsd.models import OrdenRegistro
from export_lsd.utils import (amount_txt_to_integer, exclude_eventuales,
                              get_value_from_txt, NOT_OS_INSSJP, NOT_SIJP,
                              just_eventuales, sync_format)


def process_reg1(cuit: str, pay_day: date, employees: int, export_config: dict) -> str:
    """
    Identificacion del tipo de registro	2	1	2	Alfabético
    CUIT del empleador	11	3	13	Numérico
    Identificación del envío	2	14	15	Alfanumérico
    Período	6	16	21	Numérico
    Tipo de liquidación	1	22	22	Alfanumérico
    Número de liquidación	5	23	27	Numérico
    Dias base	2	28	29	Alfanumérico
    Cantidad de trabajadores informados en registros '04'	6	30	35	Numérico
    """

    resp = f'01{cuit}SJ'
    resp += pay_day.strftime('%Y%m')
    resp += 'M00001'

    ds_base = export_config['dias_base']
    resp += str(ds_base).zfill(2) + str(employees).zfill(6)

    if len(resp) != 35:
        resp = f'Error: Longitud incorrecta ({len(resp)})'

    return resp


def process_reg2(txt_info: str, payday: date, export_config: dict) -> str:
    """
    Identificacion del tipo de registro	2	1	2
    CUIL del trabajador	11	3	13
    Legajo del trabajador	10	14	23
    Dependencia de revista del trabajador	50	24	73
    CBU de acreditación del pago	22	74	95
    Cantidad de días para proporcionar tope	3	96	98
    Fecha de pago	8	99	106
    Fecha de rúbrica	8	107	114
    Forma de pago	1	115	115
    """
    resp = []
    leg = 1
    for legajo in txt_info:
        cuil = get_value_from_txt(legajo, 'CUIL')
        area = export_config['area'].ljust(50)
        fecha_pago = payday.strftime('%Y%m%d')
        forma_pago = export_config['forma_pago']
        cbu = " " * 22
        fecha_rubrica = " " * 8

        item = f'02{cuil}{str(leg).zfill(10)}{area}{cbu}030{fecha_pago}{fecha_rubrica}{forma_pago}'
        leg += 1

        resp.append(item)

    resp_final = '\r\n'.join(resp)

    return resp_final


def process_reg3(txt_info: str, export_config: dict) -> str:
    """
    Identificación del tipo de registro	2	1	2
    CUIL del trabajador	11	3	13
    Código de concepto liquidado por el empleador	10	14	23
    Cantidad	5	24	28
    Unidades	1	29	29
    Importe	15	30	44
    Indicador Débito / Crédito	1	45	45
    Período de ajuste retroactivo	6	46	51
    """
    resp = []
    leg = 1
    for legajo in txt_info:
        cuil = get_value_from_txt(legajo, 'CUIL')
        mod_cont = int(get_value_from_txt(legajo, 'Código de Modalidad de Contratación'))
        cond = int(get_value_from_txt(legajo, 'Codigo de Condición'))
        convenc = get_value_from_txt(legajo, 'Trabajador Convencionado 0-No 1-Si')

        rem2 = amount_txt_to_integer(get_value_from_txt(legajo, 'Remuneración Imponible 2'))
        rem4 = amount_txt_to_integer(get_value_from_txt(legajo, 'Remuneración Imponible 4'))
        rem9 = amount_txt_to_integer(get_value_from_txt(legajo, 'Remuneración Imponible 9'))

        remun = rem2

        no_rem_especial = rem9 - remun
        no_remun = amount_txt_to_integer(get_value_from_txt(legajo, 'Conceptos no remunerativos')) - no_rem_especial
        # Detectados redondeos, lo quito
        if no_remun < 5:
            no_rem_especial += no_remun
            no_remun = 0

        ds_trab = str(amount_txt_to_integer(get_value_from_txt(legajo, 'Cantidad de días trabajados'))).zfill(5)

        ccn_sueldo = export_config['ccn_sueldo'].ljust(10)
        ccn_no_rem = export_config['ccn_no_rem'].ljust(10)
        ccn_no_osysind = export_config['ccn_no_osysind'].ljust(10)
        ccn_no_sind = export_config['ccn_no_sind'].ljust(10)
        ccn_sijp = export_config['ccn_sijp'].ljust(10)
        ccn_inssjp = export_config['ccn_inssjp'].ljust(10)
        ccn_os = export_config['ccn_os'].ljust(10)
        ccn_sindicato = export_config['ccn_sindicato'].ljust(10)
        porc_sindicato = int(export_config['porc_sindicato'])
        tipo_nr = int(export_config['tipo_nr'])

        # Sueldo
        item = f'03{cuil}{ccn_sueldo}{ds_trab}D{str(remun).zfill(15)}C{" " * 6}'
        resp.append(item)

        # No Remunerativo
        if int(no_remun) > 0:
            item = f'03{cuil}{ccn_no_rem}{ds_trab}D{str(no_remun).zfill(15)}C{" " * 6}'
            resp.append(item)

        # No Remunerativo Especial
        if int(no_rem_especial) > 0:
            if tipo_nr == 1:
                item = f'03{cuil}{ccn_no_sind}{ds_trab}D{str(no_rem_especial).zfill(15)}C{" " * 6}'
                resp.append(item)
            elif tipo_nr == 2:
                item = f'03{cuil}{ccn_no_osysind}{ds_trab}D{str(no_rem_especial).zfill(15)}C{" " * 6}'
                resp.append(item)

        # Aporte SIJP
        if mod_cont not in NOT_SIJP:
            ap_sijp = round(rem2 * 0.11)
            item = f'03{cuil}{ccn_sijp}{"0" * 5} {str(ap_sijp).zfill(15)}D{" " * 6}'
            resp.append(item)

        # Aporte INSSJP y OS
        if mod_cont not in NOT_OS_INSSJP and cond != 2:
            ap_inssjp = round(rem2 * 0.03)
            ap_os = round(rem4 * 0.03)
            item = f'03{cuil}{ccn_inssjp}{"0" * 5} {str(ap_inssjp).zfill(15)}D{" " * 6}'
            resp.append(item)
            item = f'03{cuil}{ccn_os}{"0" * 5} {str(ap_os).zfill(15)}D{" " * 6}'
            resp.append(item)

        # Aporte Sindicato
        if porc_sindicato > 0 and (convenc == '1' or convenc == 'T'):
            ap_sindicato = round((remun + no_rem_especial) * porc_sindicato / 100)
            item = f'03{cuil}{ccn_sindicato}{"0" * 5} {str(ap_sindicato).zfill(15)}D{" " * 6}'
            resp.append(item)

        leg += 1

    resp_final = '\r\n'.join(resp)

    return resp_final


def process_reg4(txt_info: str, export_config: dict) -> str:
    resp = []
    reg4_qs = OrdenRegistro.objects.filter(tiporegistro__order=4)

    for legajo in txt_info:
        linea = ''
        mod_cont = int(get_value_from_txt(legajo, 'Código de Modalidad de Contratación'))
        rem2 = amount_txt_to_integer(get_value_from_txt(legajo, 'Remuneración Imponible 2'))
        rem4 = amount_txt_to_integer(get_value_from_txt(legajo, 'Remuneración Imponible 4'))
        rem8 = amount_txt_to_integer(get_value_from_txt(legajo, 'Rem.Dec.788/05 - Rem Impon. 8'))
        rem9 = amount_txt_to_integer(get_value_from_txt(legajo, 'Remuneración Imponible 9'))
        rem10 = amount_txt_to_integer(get_value_from_txt(legajo, 'Remuneración Imponible 2'))
        detr = amount_txt_to_integer(get_value_from_txt(legajo, 'Importe a detraer Ley 27430'))

        for reg in reg4_qs:
            if reg.formatof931:
                # Si está lo vinculo puliendo formato
                tmp_linea = sync_format(get_value_from_txt(legajo, reg.formatof931.name), reg.long, reg.type)
                if (reg.formatof931.name == 'Cónyuge' or
                        reg.formatof931.name == 'Trabajador Convencionado 0-No 1-Si' or
                        reg.formatof931.name == 'Seguro Colectivo de Vida Obligatorio' or
                        reg.formatof931.name == 'Marca de Corresponde Reducción'):

                    tmp_linea = tmp_linea.replace('T', '1').replace('F', '0')

                linea += tmp_linea

            else:
                # Si no está, cargo los casos específicos y dejo vacío el resto (0 números y " " texto)
                if reg.name == 'Identificación del tipo de registro':
                    linea += '04'
                elif reg.name == 'Base imponible 10':
                    rem10 = rem10 - detr

                    if detr == 0 or mod_cont in NOT_SIJP:
                        rem10 = 0

                    linea += str(rem10).zfill(15)
                elif reg.name == 'Base para el cálculo diferencial de aporte de obra social y FSR (1)':
                    # Valido R4
                    # R4 = Rem + NR OS y Sind + Ap.Ad.OS
                    # Ap.Ad.OS = R4 - Rem - NR OS y Sind
                    tipo_nr = export_config['tipo_nr']
                    resta = rem2 if tipo_nr != '2' else rem9
                    aa_os = rem4 - resta
                    linea += str(aa_os).zfill(15)

                elif reg.name == 'Base para el cálculo diferencial de contribuciones de obra social y FSR (1)':
                    # Valido R8
                    # R8 = Rem + NR OS y Sind + Ct.Ad.OS
                    # Ct.Ad.OS = R8 - Rem - NR OS y Sind
                    tipo_nr = export_config['tipo_nr']
                    resta = rem2 if tipo_nr != '2' else rem9
                    aa_os = rem8 - resta
                    linea += str(aa_os).zfill(15)

                else:
                    linea += "0" * reg.long

        resp.append(linea)

    resp_final = '\r\n'.join(resp)

    return resp_final


def process_reg5(txt_info: str, export_config: dict) -> str:
    """
    Identificacion del tipo de registro	2	1	2
    CUIL del trabajador	11	3	13
    Categoría profesional	6	14	19
    Puesto desempeñado	4	20	23
    Fecha de ingreso	8	24	31
    Fecha de egreso	8	32	39
    Remuneración	15	40	54
    CUIT del empleador	11	55	65
    """
    resp = []
    for legajo in txt_info:
        cuil = get_value_from_txt(legajo, 'CUIL')
        cuit_emp = export_config['cuit_empleador_eventuales']
        rem9 = amount_txt_to_integer(get_value_from_txt(legajo, 'Remuneración Imponible 9'))

        item = f'05{cuil}     1   12022010199991231{str(rem9).zfill(15)}{cuit_emp}'

        resp.append(item)

    resp_final = '\r\n'.join(resp)

    return resp_final


def export_txt(txt_file, cuit: str, pay_day: date, export_config: dict) -> str:
    temp_sp = txt_file.split('/')
    txt_output_file = f'{("/").join(temp_sp[:-1])}/exp_{temp_sp[-1]}'

    with open(txt_file, encoding='latin-1') as f:
        txt_info = f.readlines()

    txt_clean_info = [x for x in txt_info if len(x) > 2]
    txt_no_eventuales = exclude_eventuales(txt_clean_info)
    txt_just_eventuales = just_eventuales(txt_clean_info)

    reg1 = process_reg1(cuit, pay_day, len(txt_clean_info), export_config)
    reg2 = process_reg2(txt_no_eventuales, pay_day, export_config)
    reg3 = process_reg3(txt_no_eventuales, export_config)
    reg4 = process_reg4(txt_clean_info, export_config)
    reg5 = process_reg5(txt_just_eventuales, export_config) if txt_just_eventuales else ''

    final_result = reg1 + '\r\n' + reg2 + '\r\n' + reg3 + '\r\n' + reg4
    if reg5:
        final_result += '\r\n' + reg5

    with open(txt_output_file, 'w', encoding='cp1252') as f:
        f.write(final_result)

    return txt_output_file
