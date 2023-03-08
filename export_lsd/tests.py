from django.contrib.auth.models import User
from django.test import Client, TestCase

from export_lsd.exceptions import CuitValidationException, NameValidationException
from export_lsd.models import Empleado, Empresa


class EmpresaTesting(TestCase):
    """ Testing para Empresas
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='12345')

    def test_create_empresa_ok(self):
        this_empresa = Empresa.objects.create(name='Empresa 1', cuit='30999999991', user=self.user)
        self.assertTrue(isinstance(this_empresa, Empresa))
        self.assertEqual(str(this_empresa), 'Empresa 1')

    def test_create_empresa_long_name(self):
        long_name = "a" * 121
        with self.assertRaisesMessage(NameValidationException, "El nombre es demasiado largo"):
            Empresa.objects.create(name=long_name, cuit='30999999991', user=self.user)

    def test_create_empresa_empty_name(self):
        with self.assertRaisesMessage(NameValidationException, "El nombre debe ser una cadena de texto"):
            Empresa.objects.create(name='', cuit='30999999991', user=self.user)

    def test_create_empresa_wrong_type_name(self):
        with self.assertRaisesMessage(NameValidationException, "El nombre debe ser una cadena de texto"):
            Empresa.objects.create(name=['Nombre en lista'], cuit='30999999991', user=self.user)

    def test_create_empresa_long_cuit(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIT debe tener 11 caracteres"):
            Empresa.objects.create(name="Empresa 1", cuit='123456789012', user=self.user)

    def test_create_empresa_short_cuit(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIT debe tener 11 caracteres"):
            Empresa.objects.create(name="Empresa 1", cuit='1234567890', user=self.user)

    def test_create_empresa_not_numeric_cuit(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIT debe contener sólo valores numéricos"):
            Empresa.objects.create(name="Empresa 1", cuit='30a30002012', user=self.user)

    def test_create_empresa_empty_cuit(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIT debe tener 11 caracteres"):
            Empresa.objects.create(name="Empresa 1", cuit='', user=self.user)


class EmpleadoTesting(TestCase):
    """ Testing para Empleado
    """
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(username='testuser', password='12345')
        self.empresa = Empresa.objects.create(name='Empleado 1', cuit='30999999991', user=self.user)

    def test_create_empleado_ok(self):
        expected_value = f'Empleado 1 - L.1: {self.empresa}'
        this_empleado = Empleado.objects.create(leg=1, empresa=self.empresa, name='Empleado 1', cuil='20999999991')
        self.assertTrue(isinstance(this_empleado, Empleado))
        self.assertEqual(str(this_empleado), expected_value)

    def test_create_empleado_long_name(self):
        long_name = "a" * 121
        with self.assertRaisesMessage(NameValidationException, "El nombre es demasiado largo"):
            Empleado.objects.create(leg=1, empresa=self.empresa, name=long_name, cuil='20999999991')

    def test_create_empleado_empty_name(self):
        with self.assertRaisesMessage(NameValidationException, "El nombre debe ser una cadena de texto"):
            Empleado.objects.create(leg=1, empresa=self.empresa, name='', cuil='20999999991')

    def test_create_empleado_wrong_type_name(self):
        with self.assertRaisesMessage(NameValidationException, "El nombre debe ser una cadena de texto"):
            Empleado.objects.create(leg=1, empresa=self.empresa, name=['Nombre en lista'], cuil='20999999991')

    def test_create_empleado_long_cuil(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIL debe tener 11 caracteres"):
            Empleado.objects.create(leg=1, empresa=self.empresa, name="Empleado 1", cuil='123456789012')

    def test_create_empleado_short_cuil(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIL debe tener 11 caracteres"):
            Empleado.objects.create(leg=1, empresa=self.empresa, name="Empleado 1", cuil='1234567890')

    def test_create_empresa_not_numeric_cuil(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIL debe contener sólo valores numéricos"):
            Empleado.objects.create(leg=1, empresa=self.empresa, name="Empleado 1", cuil='30a30002012')

    def test_create_empleado_empty_cuit(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIL debe tener 11 caracteres"):
            Empleado.objects.create(leg=1, empresa=self.empresa, name="Empleado 1", cuil='')
