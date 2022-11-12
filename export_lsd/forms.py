from django.forms import (DateField, DateInput, Field, FileField, FileInput,
                          ModelForm, Select, TextInput,
                          ValidationError)

from export_lsd.models import BasicExportConfig, Empresa, Empleado, Liquidacion, Presentacion
from export_lsd.tools.import_empleados import is_positive_number


class CuitCuilField(Field):
    def validate(self, value):
        """Check if value consists 11 numeric positive values"""
        # Use the parent's handling of required fields, etc.
        super().validate(value)
        if not is_positive_number(str(value)) or len(str(value)) != 11:
            raise ValidationError("Ingrese un valor numerico de 11 dígitos")


class EmpresaForm(ModelForm):
    cuit = CuitCuilField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Empresa
        fields = '__all__'
        exclude = ['user']

        widgets = {
            'name': TextInput(
                attrs={
                    'placeholder': "Ingrese el nombre de empresa"
                }
            ),
            'cuit': TextInput
            (
                attrs={
                    'placeholder': "Ingrese el número de CUIT",
                    'maxlength': 15,
                }
            )
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class EmpleadoForm(ModelForm):
    cuil = CuitCuilField()

    class Meta:
        model = Empleado
        fields = '__all__'

        widgets = {
            'empleado.name': TextInput(
                attrs={
                    'placeholder': 'Ingrese el nombre del empleado',
                }
            ),
            'empleado.cuil': TextInput(
                attrs={
                    'placeholder': "Ingrese el número de CUIL"
                }
            ),
            'empleado.area': TextInput(
                attrs={
                    'placeholder': "Ingrese el Área de Trabajo del Empleado"
                }
            )
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ConfigEBForm(ModelForm):
    class Meta:
        model = BasicExportConfig
        fields = '__all__'
        exclude = ['user']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class PeriodoForm(ModelForm):
    txtF931 = FileField(
        widget=FileInput(
            attrs={
                'class': 'form-control mb-3',
                'accept': '.txt'
            }),
        label='txt F.931',
        required=False)

    class Meta:
        model = Presentacion
        fields = ['periodo', 'empresa', 'txtF931']

        widgets = {
            'empresa': Select(
                attrs={
                    'class': "form-select mb-3"
                }
            ),
            'periodo': DateInput(
                attrs={
                    'placeholder': "MM/YYYY",
                    'type': "month",
                    'class': "form-select mb-3"
                }
            ),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class LiquidacionForm(ModelForm):
    nroLiq = Select()
    xlsx_liq = FileField(
        widget=FileInput(
            attrs={
                'class': 'form-control mb-3',
                'accept': '.xlsx'
            }),
        label='Seleccione planilla liquidación')

    payday = DateField(
        widget=DateInput(
            format="%d/%m/%Y",
            attrs={
                'placeholder': "DD/MM/YYYY",
                'class': "datepicker form-select mb-3 text-center"
            }),
        )

    class Meta:
        model = Liquidacion

        fields = ['payday', 'nroLiq', 'tipo_liq', 'xlsx_liq']

        widgets = {
            'nroLiq': Select(
                attrs={
                    'class': "form-select mb-3"
                }
            ),
            'tipo_liq': Select(
                attrs={
                    'class': "form-select mb-3"
                }
            ),
        }
