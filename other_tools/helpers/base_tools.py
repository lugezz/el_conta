import xlsxwriter


def dictionary_to_excel(data_dictionary: dict, filename: str, columns_format={}):
    """
        Export a dictionary to an excel file

        Format of the data_dictionary:
        {
            'headers' = ['header1', 'header2', ...],
            'data' = [
                {
                    'header1': 'value1',
                    'header2': 'value2',
                    ...
                },
                ...
            ]
        }

        Format of the columns_format:
        {
            'header1': {'title': 'Different Header, 'format': 'date', 'format_string': 'yyyy-mm-dd'},
            'header2': {'format': 'number', 'format_string': '#,##0.00'},
            ...
        }
    """
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})

    headers = data_dictionary['headers']
    # update headers with the specific titles
    formatted_headers = []
    for header in headers:
        if header in columns_format:
            formatted_headers.append(columns_format[header].get('title', header))
        else:
            formatted_headers.append(header)

    for col, formatted_headers in enumerate(formatted_headers):
        worksheet.write(0, col, formatted_headers, bold)
    # Add formats to the columns
    for col, header in enumerate(headers):
        if header in columns_format:
            if 'format' in columns_format[header]:
                if columns_format[header]['format'] == 'date':
                    format_string = columns_format[header].get('format_string', 'yyyy-mm-dd')
                    date_format = workbook.add_format({'num_format': format_string})
                    worksheet.set_column(col, col, None, date_format)
                elif columns_format[header]['format'] == 'number':
                    format_string = columns_format[header].get('format_string', '#,##0.00')
                    number_format = workbook.add_format({'num_format': format_string})
                    worksheet.set_column(col, col, None, number_format)

    # Iterate over the data and write it out row by row.
    for row, obj in enumerate(data_dictionary['data']):
        for col, field in enumerate(headers):
            # Puede que el campo no exista en el objeto para esta línea
            value = obj.get(field)
            if value is None:
                value = ''
            worksheet.write(row + 1, col, value)

    workbook.close()
