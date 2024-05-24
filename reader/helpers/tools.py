
def get_value_from_list(list_of_values: list, value_name: str):
    resp = ''

    for value in list_of_values:
        if value['@nombre'] == value_name:
            resp = value['@valor']

    return resp


def get_nombre_y_valor(item: str, nombre_motivo: str = 'motivo', nombre_mes: str = 'mes') -> tuple:
    """ Obtiene el nombre y el valor de un item con este formato:
       [{'@nombre': 'motivo', '@valor': '2'}, {'@nombre': 'mes', '@valor': '1'}]
       retorno (motivo, mes)
    """
    motivo = ''
    mes = ''

    for i in item:
        if i['@nombre'] == nombre_motivo:
            motivo = i['@valor']
        if i['@nombre'] == nombre_mes:
            mes = i['@valor']

    return motivo, mes


def get_list_of_values_from_list(list_of_values: list, value_list: list) -> dict:
    """ Obtiene una lista de valores de un item con este formato
        [{'@nombre': 'motivo', '@valor': '2'}, {'@nombre': 'mes', '@valor': '1'}]
        Devolviendo cada campo informado en value_list
    """
    resp = {}

    for value in value_list:
        resp[value] = get_value_from_list(list_of_values, value)

    return resp
