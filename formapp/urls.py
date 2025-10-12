# formapp/urls.py
from django.urls import path
from formapp.views import FormularioListCreateAPI, FormularioDetailAPI

urlpatterns = [
    path('', FormularioListCreateAPI.as_view(), name='form_list_create'),
    path('<str:id>/', FormularioDetailAPI.as_view(), name='form_detail'),
]