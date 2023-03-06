from django.contrib.auth.models import User
from django.test import Client, TestCase

from export_lsd.models import Empresa


class ModelTesting(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(username='testuser', password='12345')
        self.user.save()
        self.empresa = Empresa.objects.create(name='Empresa 1', cuit='30999999991', user=self.user)

    def test_post_model(self):
        this_empresa = self.empresa
        self.assertTrue(isinstance(this_empresa, Empresa))
        self.assertEqual(str(this_empresa), 'Empresa 1')
