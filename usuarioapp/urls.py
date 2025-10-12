# usuarioapp/urls.py
from django.urls import path
from usuarioapp.views import UsuarioListCreateAPI, UsuarioDetailAPI

urlpatterns = [
    path('', UsuarioListCreateAPI.as_view(), name='usuarios_list_create'),
    path('<str:id>/', UsuarioDetailAPI.as_view(), name='usuarios_detail'),
]
