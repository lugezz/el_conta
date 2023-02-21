from django.contrib import admin

from export_lsd.models import (BasicExportConfig, ConceptoLiquidacion, Empleado, Empresa,
                               Formato931, Liquidacion, OrdenRegistro,
                               Presentacion, TipoRegistro)


admin.site.register(BasicExportConfig)
admin.site.register(ConceptoLiquidacion)
admin.site.register(Formato931)
admin.site.register(Liquidacion)
admin.site.register(OrdenRegistro)
admin.site.register(Presentacion)
admin.site.register(TipoRegistro)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("leg", "name", "empresa", "cuil", "area")
    list_filter = ("empresa", "area")
    list_per_page = 30


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("name", "cuit", "user")
    list_filter = ("user", )
    list_per_page = 30
