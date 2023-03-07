from django.contrib.auth.models import User
from django.test import Client, TestCase

from export_lsd.exceptions import CuitValidationException, NameValidationException
from export_lsd.models import Empresa


class EmpresaTesting(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(username='testuser', password='12345')
        self.user.save()

    def test_create_empresa_ok(self):
        this_empresa = Empresa.objects.create(name='Empresa 1', cuit='30999999991', user=self.user)
        self.assertTrue(isinstance(this_empresa, Empresa))
        self.assertEqual(str(this_empresa), 'Empresa 1')

    def test_create_empresa_long_name(self):
        long_name = "a" * 121
        with self.assertRaisesMessage(NameValidationException, "El nombre es demasiado largo"):
            Empresa.objects.create(name=long_name, cuit='30999999991', user=self.user)

    def test_create_empresa_long_cuit(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIT debe tener 11 caracteres"):
            Empresa.objects.create(name="Empresa 1", cuit='123456789012', user=self.user)

    def test_create_empresa_short_cuit(self):
        with self.assertRaisesMessage(CuitValidationException, "El CUIT debe tener 11 caracteres"):
            Empresa.objects.create(name="Empresa 1", cuit='1234567890', user=self.user)
