from django.core.exceptions import ValidationError


class NameValidationException(ValidationError):
    pass


class CuitValidationException(ValidationError):
    pass
