from collections import defaultdict

from crum import get_current_user
from django.apps import apps
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django.forms.models import model_to_dict

DATA_TYPE = [
    ('AL', 'Alfabético'),
    ('AN', 'Alfanumérico'),
    ('NU', 'Numérico'),
]

FORMAS_PAGO = [
    ('1', 'Efectivo'),
    ('2', 'Cheque'),
    ('3', 'Acreditación'),
]

TIPO_NR = [
    ('0', 'Sólo NR'),
    ('1', 'Base Sindicato'),
    ('2', 'Base Sindicato y Obra Social')
]

TIPO_LIQ = [
    ('M', 'Mes'),
    ('Q', 'Quincena'),
    ('D', 'Días'),
    ('H', 'Horas')
]


class TipoRegistro(models.Model):
    name = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{str(self.order)}: {self.name}'

    class Meta:
        ordering = ['order']


class Formato931(models.Model):
    name = models.CharField(max_length=150)
    fromm = models.PositiveSmallIntegerField()
    long = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{str(self.name)} - From: {self.fromm}'

    class Meta:
        ordering = ['fromm']


class OrdenRegistro(models.Model):
    tiporegistro = models.ForeignKey(TipoRegistro, on_delete=models.CASCADE)
    formatof931 = models.ForeignKey(Formato931, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=120)
    fromm = models.PositiveSmallIntegerField()
    long = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=2, choices=DATA_TYPE, default='AN')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        has_f931 = '' if not self.formatof931 else ' (Link F931)'

        return f'{str(self.tiporegistro.order)} - From: {self.fromm} - {self.name}{has_f931}'

    class Meta:
        ordering = ['tiporegistro__order', 'fromm']


class Empresa(models.Model):
    name = models.CharField(max_length=120, verbose_name='Razon Social')
    cuit = models.CharField(max_length=11, validators=[MinLengthValidator(11)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.user = user
        self.user = user
        return super().save(force_insert, force_update, using, update_fields)

    def toJSON(self):
        item = model_to_dict(self)
        return item


class Empleado(models.Model):
    leg = models.PositiveSmallIntegerField()
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, verbose_name='Nombre', null=True, blank=True)
    cuil = models.CharField(max_length=11, validators=[MinLengthValidator(11)])
    area = models.CharField(max_length=120, verbose_name='Área de Trabajo', null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.empresa.name} - L.{self.leg}: {self.name}'

    def toJSON(self):
        item = model_to_dict(self)
        item['empresa'] = self.empresa.name
        return item

    class Meta:
        ordering = ['empresa__name', 'leg']
        unique_together = (('leg', 'empresa'),)


class Presentacion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    periodo = models.DateField()
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    employees = models.PositiveSmallIntegerField(default=0)
    remunerativos = models.FloatField(default=0.0)
    no_remunerativos = models.FloatField(default=0.0)
    closed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def periodo_str(self):
        return self.periodo.strftime('%Y%m')

    def __str__(self) -> str:
        return f'{self.empresa.name} - {self.periodo.strftime("%Y/%m")} '

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.user = user
        self.user = user
        return super().save(force_insert, force_update, using, update_fields)

    def get_children(self):
        return Liquidacion.objects.filter(presentacion=self).count()

    def get_download_url(self):
        this_user = get_current_user().username
        cuit = self.empresa.cuit
        periodo = self.periodo.strftime('%Y%m')
        extension = 'zip' if self.get_children() > 1 else 'txt'

        return f'temp/finaltxt_{this_user}_{cuit}_{periodo}.{extension}'

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name_plural = 'Presentaciones'


class Liquidacion(models.Model):
    nroLiq = models.PositiveSmallIntegerField(default=1)
    presentacion = models.ForeignKey(Presentacion, on_delete=models.CASCADE)
    payday = models.DateField()
    employees = models.PositiveSmallIntegerField(default=0)
    remunerativos = models.FloatField(default=0.0)
    no_remunerativos = models.FloatField(default=0.0)
    tipo_liq = models.CharField(max_length=1, choices=TIPO_LIQ, default='M', verbose_name='Tipo Liq.')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.presentacion.empresa.name} - {self.presentacion.periodo.strftime("%Y/%m")} - Liq. {self.nroLiq}'

    class Meta:
        verbose_name_plural = 'Liquidaciones'
        unique_together = (('nroLiq', 'presentacion'),)


class ConceptoLiquidacion(models.Model):
    liquidacion = models.ForeignKey(Liquidacion, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    concepto = models.CharField(max_length=10)
    cantidad = models.PositiveSmallIntegerField(default=0)
    importe = models.FloatField(default=0)
    tipo = models.CharField(max_length=4, verbose_name='Tipo de Concepto', default="Rem")

    def __str__(self) -> str:
        return f'Leg.{self.empleado.leg} - Conc:{self.concepto} - $ {self.importe}'

    class Meta:
        verbose_name_plural = 'ConceptoLiquidaciones'


class BasicExportConfig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, verbose_name='Nombre')
    dias_base = models.PositiveSmallIntegerField(default=30, verbose_name='Días Base')
    forma_pago = models.CharField(max_length=1, choices=FORMAS_PAGO, default='1', verbose_name='Forma de Pago')
    ccn_sueldo = models.CharField(max_length=20, verbose_name='Concepto Sueldo')
    ccn_no_rem = models.CharField(max_length=20, null=True, blank=True, verbose_name='Concepto NR')
    ccn_no_osysind = models.CharField(max_length=20, null=True, blank=True, verbose_name='Concepto NR OS y Sind')
    ccn_no_sind = models.CharField(max_length=20, null=True, blank=True, verbose_name='Concepto NR Sind.')
    ccn_sijp = models.CharField(max_length=20, verbose_name='Concepto SIJP')
    ccn_inssjp = models.CharField(max_length=20, verbose_name='Concepto INSSJP')
    ccn_os = models.CharField(max_length=20, verbose_name='Concepto OS')
    ccn_sindicato = models.CharField(max_length=20, null=True, blank=True, verbose_name='Concepto Sindicato')
    porc_sindicato = models.FloatField(default=0, verbose_name='Porcentaje Sindicato')
    tipo_nr = models.CharField(max_length=1, choices=TIPO_NR, default='2', verbose_name='Tipo NR')
    area = models.CharField(max_length=120, default='Administración', verbose_name='Área de Trabajo')
    cuit_empleador_eventuales = models.IntegerField(null=True, blank=True, verbose_name='CUIT Empresa Eventual')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.user = user
        self.user = user
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f'{self.user} - {self.name}'

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        unique_together = (('user', 'name'),)


class BulkCreateManager(object):
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))
