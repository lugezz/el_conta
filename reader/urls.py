from django.urls import path

from .views import (
    archivo_solo_view, detalle_presentacion,
    no_autorizado,
    procesa_hist_view, siradig_view,
    )

urlpatterns = [
    path('', siradig_view, name='siradig'),
    path('no-autorizado/', no_autorizado, name='no_autorizado'),
    path('presentaciones/<int:id>/', detalle_presentacion, name='presentaciones'),
    path('procesa/', procesa_hist_view, name='procesa-siradig'),
    path('procesa_historico/<int:id>/', procesa_hist_view, name='procesa-siradig-hist'),
    path('solo/<slug>/', archivo_solo_view, name='archivoxml'),
]
