# usuarioapp/serializers.py
from rest_framework import serializers
from usuarioapp.models import Usuario, Empresa, Perfil
from datetime import datetime


class EmpresaSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=True)
    telefono = serializers.IntegerField(required=False)
    nit = serializers.CharField(required=False)


class PerfilSerializer(serializers.Serializer):
    avatar_url = serializers.CharField(required=False, allow_blank=True)
    idioma = serializers.CharField(required=False, allow_blank=True)
    timezone = serializers.CharField(required=False, allow_blank=True)

class UsuarioSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    nombre = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    clave_hash = serializers.CharField(required=True)
    fecha_registro = serializers.DateTimeField(read_only=True)
    empresa = EmpresaSerializer(required=False)
    perfil = PerfilSerializer(required=False)

    def create(self, validated_data):
        empresa_data = validated_data.pop('empresa', None)
        perfil_data = validated_data.pop('perfil', None)

        usuario = Usuario(**validated_data)
        usuario.fecha_registro = datetime.utcnow()

        if empresa_data:
            usuario.empresa = Empresa(**empresa_data)
        if perfil_data:
            usuario.perfil = Perfil(**perfil_data)

        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "empresa" and value:
                instance.empresa = Empresa(**value)
            elif attr == "perfil" and value:
                instance.perfil = Perfil(**value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance
