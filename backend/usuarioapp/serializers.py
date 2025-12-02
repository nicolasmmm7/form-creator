# usuarioapp/serializers.py
from rest_framework import serializers
from usuarioapp.models import Usuario, Empresa, Perfil
from datetime import datetime, timedelta


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
    nombre = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    clave_hash = serializers.CharField(required=False)
    fecha_registro = serializers.DateTimeField(read_only=True)
    empresa = EmpresaSerializer(required=False)
    perfil = PerfilSerializer(required=False)

    def create(self, validated_data):
        empresa_data = validated_data.pop('empresa', None)
        perfil_data = validated_data.pop('perfil', None)

        usuario = Usuario(**validated_data)
        usuario.fecha_registro = datetime.now()

        if empresa_data:
            usuario.empresa = Empresa(**empresa_data)
        if perfil_data:
            usuario.perfil = Perfil(**perfil_data)

        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        # Permitir actualización parcial de campos simples
        for attr, value in validated_data.items():
            if attr == "empresa" and value:
                # Actualizar o crear campos dentro de empresa
                if instance.empresa:
                    for key, val in value.items():
                        setattr(instance.empresa, key, val)
                else:
                    instance.empresa = Empresa(**value)
            elif attr == "perfil" and value:
                # Actualizar o crear campos dentro de perfil
                if instance.perfil:
                    for key, val in value.items():
                        setattr(instance.perfil, key, val)
                else:
                    instance.perfil = Perfil(**value)
            else:
                setattr(instance, attr, value)

        instance.save()
        return instance


class ResetPasswordTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True)
    expires_at = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        # Si no se envía expires_at, se establece por defecto (10 minutos)
        if 'expires_at' not in validated_data:
            validated_data['expires_at'] = datetime.now() + timedelta(minutes=10)
        token = ResetPasswordToken(**validated_data)
        token.save()
        return token

    def update(self, instance, validated_data):
        # Actualiza campos existentes
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance