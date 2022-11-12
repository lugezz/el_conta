from django.contrib import admin

from export_lsd.models import (BasicExportConfig, ConceptoLiquidacion, Empleado, Empresa,
                               Formato931, Liquidacion, OrdenRegistro,
                               Presentacion, TipoRegistro)


admin.site.register(BasicExportConfig)
admin.site.register(ConceptoLiquidacion)
admin.site.register(Empleado)
admin.site.register(Empresa)
admin.site.register(Formato931)
admin.site.register(Liquidacion)
admin.site.register(OrdenRegistro)
admin.site.register(Presentacion)
admin.site.register(TipoRegistro)
