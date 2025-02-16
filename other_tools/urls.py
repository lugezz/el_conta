from django.urls import path

from other_tools.views import import_pem


urlpatterns = [
    path('pem-a-excel/', import_pem, name='pem-a-excel'),
]
