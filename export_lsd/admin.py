from django.contrib import admin

from export_lsd.models import (BasicExportConfig, ConceptoLiquidacion, Empleado, Empresa,
                               Formato931, Liquidacion, OrdenRegistro,
                               Presentacion, TipoRegistro)


admin.site.register(ConceptoLiquidacion)
admin.site.register(Formato931)
admin.site.register(Liquidacion)
admin.site.register(OrdenRegistro)
admin.site.register(TipoRegistro)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("leg", "name", "empresa", "cuil", "area", "actualizado", "actualizado_por")
    list_filter = ("empresa", "area")
    list_per_page = 30
    search_fields = ("leg", "name", "empresa__name", "cuil")

    @admin.display(empty_value='unknown')
    def actualizado(self, obj):
        return obj.updated.strftime('%Y/%m/%d')

    @admin.display(empty_value='unknown')
    def actualizado_por(self, obj):
        return obj.updated_by


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("name", "cuit", "user", "view_created")
    list_filter = ("user", )
    list_per_page = 30

    @admin.display(empty_value='unknown')
    def view_created(self, obj):
        return obj.created.strftime('%Y/%m/%d')


@admin.register(BasicExportConfig)
class BasicExportConfigAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "dias_base")
    list_filter = ("user", )
    list_per_page = 30


@admin.register(Presentacion)
class PresentacionAdmin(admin.ModelAdmin):
    list_display = ("periodo_str", "empresa", "user", "creado", "actualizado")
    list_filter = ("user", )
    list_per_page = 30

    @admin.display(empty_value='unknown')
    def creado(self, obj):
        return obj.created.strftime('%Y/%m/%d')

    @admin.display(empty_value='unknown')
    def actualizado(self, obj):
        return obj.updated.strftime('%Y/%m/%d')
