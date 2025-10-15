# usuarioapp/urls.py
from django.urls import path
from usuarioapp.views import (
    UsuarioListCreateAPI,
    UsuarioDetailAPI,
    hello,
    protected_view,
    UsuarioLoginAPI,
    firebase_auth_sync)
from . import views


urlpatterns = [
    #endpoints de usuarios
    path('hello/', hello, name='hello'),
    path('protected/', views.protected_view, name='protected_view'),
    #endpoint de prueba de autenticación con Firebase
    path('auth/firebase/', views.firebase_auth_sync, name='firebase_auth_sync'),
    path('login/', UsuarioLoginAPI.as_view(), name='usuarios_login'),  # 👈 esta va antes de la que usa <str:id>
    path('', UsuarioListCreateAPI.as_view(), name='usuarios_list_create'),
    path('<str:id>/', UsuarioDetailAPI.as_view(), name='usuarios_detail'),

    
    
   
]