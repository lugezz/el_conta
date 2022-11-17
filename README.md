# Siradig Reader

Siradig Reader fue desarrollado con la finalidad de simplificar
el proceso de lectura masiva de formularios Siradig de AFIP de los empleados.

## Uso

Para detalles de como iniciar tu entorno local de desarrollo, ingresa [aqui](docs/entorno-local.md)

## SMTP Config
Para que esta aplicacion sea capaz de enviar emails debes actualizar el archivo `local_settings.py`
con las referencias a tu servidor SMTP.

```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.sendinblue.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'tu usuaurio'
EMAIL_HOST_PASSWORD = 'tu clave'
```

## Contribuciones
Son siempre bienvenidas las Pull Requests, para cambios mayores por favor abra un Issue primero para discutir la propuesta del cambio

Por favor asegurese de actualizar los tests apropiadamente

## Licencia
[MIT](https://choosealicense.com/licenses/mit/)


---
# Exporta LSD
# Libro Sueldos Digital

### Libro Sueldos Digital - Simple exportador desde txt F.931

El objetivo es simplificar el proceso para generar el txt exportador para LSD desde txt F.931 para quienes no cuenten con un sistema para este fin.
El código es abierto para todos.


## Puntos a considerar

### Exportación Básica

_Legajos predeterminado por orden, o sea 1, 2, 3, etc. No configurable por el momento_

_Lugar de Trabajo igual para toda la nómina de acuerdo a la configuración_

_Tratamiento de todas liquidaciones mensuales o quincenales como una única liquidación mensual_

_Retroactivos no tratados_

_Pendiente tratar análisis sobre el tope_

_Eventuales: Pendiente fecha de ingreso y de egreso_

### Exportación Avanzada

_No está alcanzado el pago por CBU_

---
### Paso a paso puesta en marcha

* Crear estos registros en TipoRegistro

    1: Datos referenciales del envío (Liquidación de SyJ y datos para DJ F931)
    2: Datos referenciales de la Liquidación de SyJ del trabajador
    3: Detalle de los conceptos de sueldo liquidados al trabajador
    4: Datos del trabajador para el calculo de la DJ F931
    5: Datos del trabajador de la empresa de servicios eventuales - Dec 342/1992

* Acceder a exportadb-f931/

* Acceder a exportadb/

* Vincular registros 4 con lo detallado en F.931

---

### TODO List

#### Exportación avanzada


---

### Future versions TODO List

#### Exportación avanzada
* Agregar parametrización de conceptos para no tener la necesidad de la columna Tipo
* Eventuales
* Ver cálculo de la Base Adicional OS.
* Configurar días base
* Configurar forma de pago. No acreditación porque requiere CBU


#### Empleados
* Borrado masivo y ver si exportación conviene pisar

#### General
