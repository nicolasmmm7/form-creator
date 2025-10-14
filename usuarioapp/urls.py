# usuarioapp/urls.py
from django.urls import path
from usuarioapp.views import UsuarioListCreateAPI, UsuarioDetailAPI, UsuarioLoginAPI


urlpatterns = [
    path('login/', UsuarioLoginAPI.as_view(), name='usuarios_login'),  # 👈 esta va antes de la que usa <str:id>
    path('', UsuarioListCreateAPI.as_view(), name='usuarios_list_create'),
    path('<str:id>/', UsuarioDetailAPI.as_view(), name='usuarios_detail'),
]