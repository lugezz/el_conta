from django.conf import settings
from django.db import models


class RegAcceso(models.Model):
    reg_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return f"/siradig/procesa_historico/{self.id}/"

    def __str__(self):
        return f'{self.id} - {self.reg_user} - {self.fecha.strftime("%d/%m/%Y %H:%M")}'

    class Meta:
        ordering = ['-fecha']


class Registro(models.Model):
    id_reg = models.ForeignKey(RegAcceso, on_delete=models.CASCADE, related_name='registers')
    cuil = models.BigIntegerField()
    deduccion = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    dato1 = models.CharField(max_length=50)
    dato2 = models.CharField(max_length=50, blank=True, null=True)
    porc = models.CharField(max_length=3, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.id_reg.id} -{self.id_reg.reg_user} - {self.id_reg.fecha.strftime("%d/%m/%Y")} - {self.cuil}'

    def get_download_url(self):
        return f"/procesa_historico/{self.id_reg}/"
