from django.urls import path

from export_lsd.tools.export_db import exportaDB, exportaDB_f931
from export_lsd.tools.export_basic_txt import export_txt
from export_lsd.views import (advanced_export, advanced_export_liqs, basic_export,
                              get_final_txts, import_empleados, HomeView,
                              ConfigEBCreateView, ConfigEBDeleteView, ConfigEBListView,
                              ConfigEBUpdateView,
                              EmpleadoCreateView, EmpleadoDeleteView, EmpleadoListView,
                              EmpleadoUpdateView, EmpresaCreateView, EmpresaDeleteView,
                              EmpresaListView, EmpresaUpdateView,
                              LiquidacionDeleteView,
                              PresentacionDeleteView, PresentacionListView)

app_name = 'export_lsd'

urlpatterns = [
    # Panel
    path('', HomeView.as_view(), name='home'),

    # Empresas
    path('empresa/', EmpresaListView.as_view(), name='empresa_list'),
    path('empresa/add/', EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresa/update/<int:pk>/', EmpresaUpdateView.as_view(), name='empresa_update'),
    path('empresa/delete/<int:pk>/', EmpresaDeleteView.as_view(), name='empresa_delete'),

    # Empleados
    path('empleado/', EmpleadoListView.as_view(), name='empleado_list'),
    path('empleado/add/', EmpleadoCreateView.as_view(), name='empleado_create'),
    path('empleado/update/<int:pk>/', EmpleadoUpdateView.as_view(), name='empleado_update'),
    path('empleado/delete/<int:pk>/', EmpleadoDeleteView.as_view(), name='empleado_delete'),

    # Exportación  -------------------------------------------------------------
    # Configuración Exportación Básica
    path('config-eb/', ConfigEBListView.as_view(), name='config_eb_list'),
    path('config-eb/add/', ConfigEBCreateView.as_view(), name='config_eb_create'),
    path('config-eb/update/<int:pk>/', ConfigEBUpdateView.as_view(), name='config_eb_update'),
    path('config-eb/delete/<int:pk>/', ConfigEBDeleteView.as_view(), name='config_eb_delete'),

    # Exportaciones
    path('basic/', basic_export, name='basic'),
    path('import-empleados/', import_empleados, name='import_empleados'),

    # Advanced
    path('advanced/', advanced_export, name='advanced'),
    path('advanced/liqs/<int:pk>', advanced_export_liqs, name='advanced_liqs'),
    path('advanced/get-txts/<int:pk>', get_final_txts, name='advanced_get_txt'),
    path('advanced/delete/<int:pk>', PresentacionDeleteView.as_view(), name='advanced_delete'),
    path('advanced/liq/delete/<int:pk>', LiquidacionDeleteView.as_view(), name='advanced_liq_delete'),

    # Presentaciones
    path('presentaciones/', PresentacionListView.as_view(), name='presentacion_list'),

    # Actualizaciones BD
    path('exportadb/', exportaDB),
    path('exportadb-f931/', exportaDB_f931),
    path('export_test/', export_txt),
]
