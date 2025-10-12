from rest_framework import serializers
from formapp.models import (
    Opcion,
    Validaciones,
    Pregunta,
    ConfiguracionFormulario,
    Formulario
)
from usuarioapp.models import Usuario  # para la referencia del administrador
from usuarioapp.serializers import UsuarioSerializer

# -----------------------------
# Serializers embebidos
# -----------------------------
class OpcionSerializer(serializers.Serializer):
    valor = serializers.CharField(required=False, allow_blank=True)
    texto = serializers.CharField(required=True)
    orden = serializers.IntegerField(required=False)


class ValidacionesSerializer(serializers.Serializer):
    longitud_minima = serializers.IntegerField(required=False, allow_null=True)
    longitud_maxima = serializers.IntegerField(required=False, allow_null=True)
    valor_minimo = serializers.IntegerField(required=False, allow_null=True)
    valor_maximo = serializers.IntegerField(required=False, allow_null=True)


class PreguntaSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    tipo = serializers.CharField(required=True)
    enunciado = serializers.CharField(required=True)
    obligatorio = serializers.BooleanField(default=False)
    posicion = serializers.IntegerField(required=False)
    opciones = OpcionSerializer(many=True, required=False)
    validaciones = ValidacionesSerializer(required=False, allow_null=True)

    def validate(self, data):
        tipo = data.get("tipo")

        # --- Validaciones condicionales según tipo ---
        if tipo in ("opcion_multiple", "checkbox", "radio"):
            if not data.get("opciones"):
                raise serializers.ValidationError({
                    "opciones": "Este tipo de pregunta requiere al menos una opción."
                })

        elif tipo == "texto_libre":
            valid = data.get("validaciones")
            if not valid or (not valid.get("longitud_minima") and not valid.get("longitud_maxima")):
                raise serializers.ValidationError({
                    "validaciones": "Las preguntas de texto libre deben incluir validaciones de longitud."
                })

        elif tipo == "escala_numerica":
            valid = data.get("validaciones")
            if not valid or valid.get("valor_minimo") is None or valid.get("valor_maximo") is None:
                raise serializers.ValidationError({
                    "validaciones": "Las preguntas escalares deben tener valor_minimo y valor_maximo."
                })

        else:
            raise serializers.ValidationError({
                "tipo": f"Tipo de pregunta '{tipo}' no reconocido."
            })

        return data



class ConfiguracionFormularioSerializer(serializers.Serializer):
    privado = serializers.BooleanField(default=False)
    fecha_limite = serializers.DateTimeField(required=False, allow_null=True)
    notificaciones_email = serializers.BooleanField(default=True)
    requerir_login = serializers.BooleanField(default=True)
    una_respuesta = serializers.BooleanField(default=False)
    permitir_edicion = serializers.BooleanField(default=False)

# -----------------------------
# Serializer principal: Formulario
# -----------------------------
class FormularioSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    titulo = serializers.CharField(required=True)
    descripcion = serializers.CharField(required=False, allow_blank=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
    administrador = serializers.CharField(required=True)  # lo mapearemos con Usuario manualmente
    configuracion = ConfiguracionFormularioSerializer(required=False)
    preguntas = PreguntaSerializer(many=True, required=False)

    """def validate_preguntas(self, value):
            ids = [p["id"] for p in value]
            if len(ids) != len(set(ids)):
                raise serializers.ValidationError("Los IDs de las preguntas deben ser únicos dentro del formulario.")
            return value
            
            para comprobar que las ids no se repitan pero mas adelante papus"""

    def create(self, validated_data):
        from usuarioapp.models import Usuario
        from bson import ObjectId
        # extraer campos embebidos
        config_data = validated_data.pop('configuracion', None)
        preguntas_data = validated_data.pop('preguntas', [])
        admin_id = validated_data.pop('administrador')

        # buscar referencia al usuario administrador
        admin_ref = Usuario.objects.get(id=ObjectId(admin_id))

        formulario = Formulario(**validated_data)
        formulario.administrador = admin_ref

        # asignar configuración
        if config_data:
            formulario.configuracion = ConfiguracionFormulario(**config_data)

        # asignar preguntas embebidas
        if preguntas_data:
            formulario.preguntas = [
                Pregunta(
                    id=p['id'],
                    tipo=p['tipo'],
                    enunciado=p['enunciado'],
                    obligatorio=p.get('obligatorio', False),
                    opciones=[Opcion(**opt) for opt in p.get('opciones', [])],
                    validaciones=Validaciones(**p['validaciones'])
                    if p.get('validaciones') else None,
                    posicion=p.get('posicion', None)
                )
                for p in preguntas_data
            ]

        formulario.save()
        return formulario