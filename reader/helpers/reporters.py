import os

from django.conf import settings
import xlsxwriter

from reader.deducciones import get_deduccion

DEDUCCIONES_CON_SUBINDICE = ['32']


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
    worksheet.write(0, 0, "Pres.Vers", header_format)
    worksheet.write(0, 1, "CUIL", header_format)
    worksheet.write(0, 2, "Deducción", header_format)
    worksheet.write(0, 3, "Tipo", header_format)
    worksheet.write(0, 4, "Mes", header_format)
    worksheet.write(0, 5, "Nro.Doc", header_format)
    worksheet.write(0, 6, "Dato1", header_format)
    worksheet.write(0, 7, "Dato2", header_format)
    worksheet.write(0, 8, "Porc", header_format)
    worksheet.write(0, 9, "Descripción", header_format)

    # Algo de formato
    worksheet.set_column('A:A', 12)
    worksheet.set_column('B:B', 12)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('H:H', 12)
    worksheet.set_column('J:J', 60)
    worksheet.freeze_panes(1, 1)

    # Itero por cada item de MatrizTodo
    for item in query:
        worksheet.write(row, 0, item.presentacion_version, center_format)
        worksheet.write_number(row, 1, item.cuil, center_format)
        worksheet.write(row, 2, item.deduccion, no_format)

        if item.deduccion == 'ganLiqOtrosEmpEnt':
            worksheet.write(row, 3, item.tipo, no_format)
        else:
            val_item = 0 if not item.tipo else float(item.tipo)
            worksheet.write_number(row, 3, val_item, center_format)

        worksheet.write(row, 4, item.mes, center_format)
        worksheet.write(row, 5, item.nro_doc, center_format)

        val_item = 0 if not item.dato1 else int(item.dato1)
        worksheet.write_number(row, 6, int(val_item), center_format)

        if item.deduccion == 'cargaFamilia':
            worksheet.write_number(row, 7, int(item.dato2), center_format)
        else:
            worksheet.write_number(row, 7, float(item.dato2), money)

        val_item = 0 if not item.porc else float(item.porc)
        worksheet.write_number(row, 8, val_item, center_format)

        subindice = item.dato1 if item.tipo in DEDUCCIONES_CON_SUBINDICE else ''
        worksheet.write(row, 9, get_deduccion(item.deduccion, item.tipo, subindice), no_format)
        row += 1
    workbook.close()
