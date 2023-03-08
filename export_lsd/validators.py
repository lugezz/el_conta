from export_lsd.exceptions import CuitValidationException
from export_lsd.exceptions import NameValidationException


def validate_cuil(value):
    """ Debe tener exactamente 11 caracteres númericos """
    if len(value) != 11:
        raise CuitValidationException('El CUIL debe tener 11 caracteres')

    if not value.isdigit():
        raise CuitValidationException('El CUIL debe contener sólo valores numéricos')

    return value


def validate_cuit(value):
    """ Debe tener exactamente 11 caracteres númericos """
    if len(value) != 11:
        raise CuitValidationException('El CUIT debe tener 11 caracteres')

    if not value.isdigit():
        raise CuitValidationException('El CUIT debe contener sólo valores numéricos')

    return value


def validate_name(value):
    """ Validar que el nombre no tenga caracteres raros.
        Devolver None si no hay cambios o el nuevo nombre si aceptamos el cambio. """
    if type(value) != str or not value:
        raise NameValidationException('El nombre debe ser una cadena de texto')
    if len(value) > 120:
        raise NameValidationException('El nombre es demasiado largo')

    return value
