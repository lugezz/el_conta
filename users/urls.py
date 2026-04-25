from django.urls import path

from .views import RegisterView, profile

urlpatterns = [
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
]
