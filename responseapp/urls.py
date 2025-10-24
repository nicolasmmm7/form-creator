# responseapp/urls.py
from django.urls import path
from .views import RespuestaListCreateAPI, RespuestaDetailAPI

urlpatterns = [
    path('', RespuestaListCreateAPI.as_view(), name='respuestas-list-create'),
    path('<str:id>/', RespuestaDetailAPI.as_view(), name='respuestas-detail'),
]
