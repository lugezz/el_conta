from django import template

register = template.Library()


def currency(dollars):
    currency1 = "$ {:,.2f}".format(float(dollars))
    entero, decimales = currency1.split(".")[0], currency1.split(".")[1]
    nuevo_entero = entero.replace(",", ".")
    currency2 = f'{nuevo_entero},{decimales}'

    return currency2


register.filter('currency', currency)
