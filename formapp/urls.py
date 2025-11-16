# formapp/urls.py
from django.urls import path
from formapp.views import (
    FormularioListCreateAPI, 
    FormularioDetailAPI,
    FormularioAccesoAPI,
    FormularioAgregarUsuarioAPI,
    FormularioRemoverUsuarioAPI,
    FormularioListarUsuariosAPI
)

urlpatterns = [
    # Rutas existentes
    path('', FormularioListCreateAPI.as_view(), name='form_list_create'),
    path('<str:id>/', FormularioDetailAPI.as_view(), name='form_detail'),
    
    # Nuevas rutas para gestión de acceso
    path('<str:id>/verificar-acceso/', FormularioAccesoAPI.as_view(), name='form_verificar_acceso'),
    path('<str:id>/usuarios-autorizados/', FormularioListarUsuariosAPI.as_view(), name='form_listar_usuarios'),
    path('<str:id>/agregar-usuario/', FormularioAgregarUsuarioAPI.as_view(), name='form_agregar_usuario'),
    path('<str:id>/remover-usuario/', FormularioRemoverUsuarioAPI.as_view(), name='form_remover_usuario'),
]